"""Part 11: verify what an AI said about the flawed security draft.

Run from the project folder (after migrate):   python -m security_review.review
"""
import os
from datetime import timedelta

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_hub.settings")
django.setup()

from django.conf import global_settings, settings  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402
from django.contrib.auth.hashers import make_password  # noqa: E402
from django.core.checks import run_checks  # noqa: E402
from django.db import transaction  # noqa: E402
from django.template import Context, Template  # noqa: E402
from django.test import Client, override_settings  # noqa: E402
from django.utils import timezone  # noqa: E402

from bookings.models import Booking  # noqa: E402
from rooms.models import Room  # noqa: E402
from security_review.flawed import FLAWED_ALLOWED_HOSTS, FLAWED_TEMPLATE  # noqa: E402


def evaluate():
    """Return the facts behind each AI finding and claim. Everything happens in a transaction that is rolled back."""
    facts = {}
    host = "testserver" if "testserver" in settings.ALLOWED_HOSTS else "localhost"
    User = get_user_model()
    with transaction.atomic():
        alice = User.objects.create_user("alice", "alice@example.com", "x")
        bob = User.objects.create_user("bob", "bob@example.com", "x")
        room = Room.objects.create(name="Review Room", capacity=40)
        start = timezone.now() + timedelta(days=2)

        def booking_of_bob():
            return Booking.objects.create(room=room, owner=bob, booked_by="bob", start=start, end=start + timedelta(hours=1))

        # Finding 1: login_required alone is not authorization
        pk = booking_of_bob().pk
        client = Client(HTTP_HOST=host)
        client.force_login(alice)
        with override_settings(ROOT_URLCONF="security_review.flawed_urls"):
            client.post(f"/flawed/cancel/{pk}/")
        facts["flawed_lets_alice_delete_bobs_booking"] = not Booking.objects.filter(pk=pk).exists()

        # Finding 2: the real view hides other people's bookings
        pk = booking_of_bob().pk
        response = client.post(f"/bookings/{pk}/delete/")
        facts["real_view_status_for_alice"] = response.status_code
        facts["real_view_keeps_the_booking"] = Booking.objects.filter(pk=pk).exists()

        # Claim 5: the link is hidden for alice, yet the open URL still worked
        shown = Template(FLAWED_TEMPLATE).render(Context({"user": alice}))
        facts["link_is_hidden_for_alice"] = "Cancel" not in shown

        # Finding 3: ALLOWED_HOSTS = ["*"]
        with override_settings(ALLOWED_HOSTS=FLAWED_ALLOWED_HOSTS):
            facts["star_accepts_evil_host"] = Client(HTTP_HOST="evil.example").get("/").status_code == 200
        with override_settings(ALLOWED_HOSTS=["campus.example.com"]):
            facts["real_hosts_reject_evil_host"] = Client(HTTP_HOST="evil.example").get("/").status_code == 400
        with override_settings(ALLOWED_HOSTS=FLAWED_ALLOWED_HOSTS, DEBUG=False):
            ids = [m.id for m in run_checks(include_deployment_checks=True)]
        facts["check_deploy_is_silent_about_star"] = "security.W020" not in ids

        # Claim 6: passwords
        with override_settings(PASSWORD_HASHERS=global_settings.PASSWORD_HASHERS):  # Django's own defaults, not the fast test hasher
            facts["password_hash"] = make_password("S3cret-pass-2027").split("$")[0]
        transaction.set_rollback(True)
    return facts


def main():
    f = evaluate()
    yes = lambda b: "confirmed" if b else "NOT confirmed"  # noqa: E731
    print(f"FINDING 1  {'login_required alone lets Alice cancel Bobs booking':<56} {yes(f['flawed_lets_alice_delete_bobs_booking'])}")
    print(f"FINDING 2  {'the real view answers 404 for a booking you do not own':<56} {yes(f['real_view_status_for_alice'] == 404 and f['real_view_keeps_the_booking'])}")
    print(f"FINDING 3  {'ALLOWED_HOSTS=[*] accepts any Host; check --deploy is silent':<56} {yes(f['star_accepts_evil_host'] and f['check_deploy_is_silent_about_star'])}")
    print(f"CLAIM 4    {'login_required is enough to protect a booking':<56} {'FALSE' if f['flawed_lets_alice_delete_bobs_booking'] else 'TRUE'}")
    print(f"CLAIM 5    {'hiding the Cancel button prevents unauthorized cancels':<56} {'FALSE' if f['link_is_hidden_for_alice'] and f['flawed_lets_alice_delete_bobs_booking'] else 'TRUE'}")
    print(f"CLAIM 6    {'Django stores passwords as salted hashes by default':<56} {'TRUE' if f['password_hash'] == 'pbkdf2_sha256' else 'FALSE'}  ({f['password_hash']})")


if __name__ == "__main__":
    main()
