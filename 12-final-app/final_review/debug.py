"""Part 12: reproduce the bug report, and verify what an AI assistant said about its cause and fix."""
from datetime import datetime, timedelta, timezone as dt_timezone

from django.db import transaction
from django.test.utils import CaptureQueriesContext
from django.db import connection

from bookings.availability import available_rooms
from bookings.models import Booking
from final_review.buggy import buggy_available_rooms
from rooms.models import Room


def at(hour, day=1):
    return datetime(2027, 3, day, hour, 0, tzinfo=dt_timezone.utc)


def evaluate():
    """Bug report: 'Lab C shows as busy from 10:00 to 12:00, but it has no booking then.' Rolled back afterwards."""
    facts = {}
    with transaction.atomic():
        busy = Room.objects.create(name="Room A", capacity=40)   # booked 09:00 to 11:00
        split = Room.objects.create(name="Lab C", capacity=40)   # booked 08:00 to 09:00 and 13:00 to 14:00: free at 10:00 to 12:00
        empty = Room.objects.create(name="Open Studio", capacity=40)     # never booked
        for room, start, end in [(busy, 9, 11), (split, 8, 9), (split, 13, 14)]:
            Booking.objects.create(room=room, booked_by="x", start=at(start), end=at(end))

        mine = {busy.pk, split.pk, empty.pk}   # ignore any rooms already in the dev database
        names = lambda qs: sorted(r.name for r in qs if r.pk in mine)  # noqa: E731
        facts["buggy_10_to_12"] = names(buggy_available_rooms(at(10), at(12)))
        facts["fixed_10_to_12"] = names(available_rooms(at(10), at(12)))
        facts["buggy_back_to_back"] = names(buggy_available_rooms(at(11), at(12)))    # right after Room A's booking ends
        facts["fixed_back_to_back"] = names(available_rooms(at(11), at(12)))
        facts["with_select_related"] = names(buggy_available_rooms(at(10), at(12)).select_related())  # claim: does this fix it?
        facts["buggy_sql"] = str(buggy_available_rooms(at(10), at(12)).query)
        facts["fixed_sql"] = str(available_rooms(at(10), at(12)).query)
        with CaptureQueriesContext(connection) as ctx:
            list(available_rooms(at(10), at(12)))
        facts["fixed_query_count"] = len(ctx)
        transaction.set_rollback(True)
    return facts
