"""Part 6: verify what an AI said about the flawed routing.

Run from the project folder:   python -m routing_review.review
"""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_hub.settings")
django.setup()

from django.test import override_settings  # noqa: E402
from django.urls import NoReverseMatch, Resolver404, resolve, reverse  # noqa: E402


def raises(exception, call):
    try:
        call()
    except exception:
        return True
    return False


def evaluate():
    """Return the facts behind each AI finding and claim."""
    with override_settings(ROOT_URLCONF="routing_review.flawed_urls"):
        facts = {
            "namespace_missing": raises(NoReverseMatch, lambda: reverse("bookings:room_list")),
            "rooms_is_shadowed": resolve("/rooms/").url_name == "page",
            "unanchored_matches_extra": not raises(Resolver404, lambda: resolve("/room-2/extra/")),
        }
    with override_settings(ROOT_URLCONF="campus_hub.urls"):
        facts["fixed_reverse"] = reverse("bookings:room_list")
        facts["fixed_resolves_list"] = resolve("/rooms/").url_name == "room_list"
        facts["fixed_rejects_extra"] = raises(Resolver404, lambda: resolve("/room-2/extra/"))
    return facts


def main():
    f = evaluate()
    print(f"FINDING 1  {'No app_name: bookings:... cannot reverse':<48} {'confirmed' if f['namespace_missing'] else 'NOT confirmed'}")
    print(f"FINDING 2  {'<str:page>/ shadows /rooms/ (order matters)':<48} {'confirmed' if f['rooms_is_shadowed'] else 'NOT confirmed'}")
    print(f"FINDING 3  {'re_path without ^ and $ matches too much':<48} {'confirmed' if f['unanchored_matches_extra'] else 'NOT confirmed'}")
    print(f"CLAIM 4    {'most specific route wins, whatever the order':<48} {'FALSE' if f['rooms_is_shadowed'] else 'TRUE'}")
    print(f"CLAIM 5    {'re_path is anchored automatically':<48} {'FALSE' if f['unanchored_matches_extra'] else 'TRUE'}")
    print(f"CLAIM 6    {'include + app_name gives namespaced names':<48} {'TRUE' if f['fixed_reverse'] == '/rooms/' else 'FALSE'}  (reverse -> {f['fixed_reverse']})")


if __name__ == "__main__":
    main()
