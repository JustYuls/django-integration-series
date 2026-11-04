"""Part 7: verify what an AI said about the flawed form pieces.

Run from the project folder (after migrate):   python -m form_review.review
"""
import os
from datetime import timedelta

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_hub.settings")
django.setup()

from django.conf import settings  # noqa: E402
from django.db import transaction  # noqa: E402
from django.template import Context, Template  # noqa: E402
from django.test import Client, RequestFactory  # noqa: E402
from django.utils import timezone  # noqa: E402

from bookings.forms import LOCAL_FORMAT, BookingForm  # noqa: E402
from bookings.models import Booking, Room  # noqa: E402
from form_review.flawed import FLAWED_FORM_TEMPLATE, FLAWED_NAME_TEMPLATE, FlawedBookingForm  # noqa: E402

SCRIPT = "<script>alert(1)</script>"


def evaluate():
    """Return the facts behind each AI finding and claim. Everything happens in a transaction that is rolled back."""
    facts = {}
    with transaction.atomic():
        room = Room.objects.create(name="Review Room", capacity=40)
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        fmt = lambda dt: timezone.localtime(dt).strftime(LOCAL_FORMAT)  # noqa: E731
        data = {"room": room.pk, "booked_by": "Ana", "purpose": "", "attendees": 10, "start": fmt(start), "end": fmt(end)}

        # Finding 1: the CSRF token
        request = RequestFactory().get("/")
        from django.template import RequestContext
        flawed_page = Template(FLAWED_FORM_TEMPLATE).render(RequestContext(request, {"form": FlawedBookingForm()}))
        facts["flawed_has_token"] = "csrfmiddlewaretoken" in flawed_page
        # The test runner allows "testserver"; outside it, only localhost-style hosts are allowed while DEBUG is on.
        host = "testserver" if "testserver" in settings.ALLOWED_HOSTS else "localhost"
        facts["real_page_has_token"] = "csrfmiddlewaretoken" in Client(HTTP_HOST=host).get("/bookings/new/").content.decode()
        strict = Client(enforce_csrf_checks=True, HTTP_HOST=host)
        facts["post_without_token_status"] = strict.post("/bookings/new/", data).status_code

        # Finding 2: |safe on user text, and claim 6: escaping by default
        facts["safe_leaves_script"] = SCRIPT in Template(FLAWED_NAME_TEMPLATE).render(Context({"name": SCRIPT}))
        facts["default_escapes_script"] = SCRIPT not in Template("{{ name }}").render(Context({"name": SCRIPT}))

        # Finding 3 and claim 4: capacity and double bookings
        too_many = dict(data, attendees=60)
        facts["flawed_accepts_too_many"] = FlawedBookingForm(too_many).is_valid()
        facts["real_rejects_too_many"] = not BookingForm(too_many).is_valid()
        Booking.objects.create(room=room, booked_by="Ben", start=start, end=end)
        facts["flawed_accepts_double_booking"] = FlawedBookingForm(data).is_valid()
        facts["real_rejects_double_booking"] = not BookingForm(data).is_valid()
        transaction.set_rollback(True)
    return facts


def main():
    f = evaluate()
    yes = lambda ok: "confirmed" if ok else "NOT confirmed"  # noqa: E731
    print(f"FINDING 1  {'No {% csrf_token %}: POST gets 403':<46} {yes(not f['flawed_has_token'] and f['post_without_token_status'] == 403)}  (403)")
    print(f"FINDING 2  {'|safe on user text lets a script through':<46} {yes(f['safe_leaves_script'])}")
    print(f"FINDING 3  {'No clean(): capacity and clashes unchecked':<46} {yes(f['flawed_accepts_too_many'] and f['flawed_accepts_double_booking'])}")
    print(f"CLAIM 4    {'a ModelForm checks capacity and clashes':<46} {'FALSE' if f['flawed_accepts_too_many'] else 'TRUE'}")
    print(f"CLAIM 5    {'csrf_token is only for login forms':<46} {'FALSE' if f['post_without_token_status'] == 403 else 'TRUE'}")
    print(f"CLAIM 6    {'{{ variables }} are escaped by default':<46} {'TRUE' if f['default_escapes_script'] else 'FALSE'}")


if __name__ == "__main__":
    main()
