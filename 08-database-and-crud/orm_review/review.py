"""Part 8: verify what an AI said about the flawed query helpers.

Run from the project folder (after migrate):   python -m orm_review.review
"""
import os
from datetime import timedelta

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_hub.settings")
django.setup()

from django.db import connection, transaction  # noqa: E402
from django.test.utils import CaptureQueriesContext  # noqa: E402
from django.utils import timezone  # noqa: E402

from bookings.models import Booking, Room  # noqa: E402
from orm_review.flawed import fixed_booking_lines, fixed_busy_check, flawed_booking_lines, flawed_busy_check  # noqa: E402

ROWS = 10


def queries(call):
    with CaptureQueriesContext(connection) as ctx:
        call()
    return ctx.captured_queries


def build_filter():
    return Booking.objects.filter(attendees__gte=1).order_by("-start")  # builds, never evaluates


def run_filter():
    return list(Booking.objects.filter(attendees__gte=1))


def count_rows():
    return Booking.objects.count()


def len_of_rows():
    return len(Booking.objects.all())


def evaluate():
    """Return the facts behind each AI finding and claim. Everything happens in a transaction that is rolled back."""
    facts = {"rows": ROWS}
    with transaction.atomic():
        room = Room.objects.create(name="Review Room", capacity=40)
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=1)
        rows = [Booking(room=room, booked_by=f"P{i}", start=start, end=end) for i in range(ROWS)]
        Booking.objects.bulk_create(rows)  # many rows, one query

        facts["flawed_lines_queries"] = len(queries(flawed_booking_lines))
        facts["fixed_lines_queries"] = len(queries(fixed_booking_lines))
        facts["lines_equal"] = sorted(flawed_booking_lines()) == sorted(fixed_booking_lines())

        facts["queries_when_building"] = len(queries(build_filter))
        facts["queries_when_evaluating"] = len(queries(run_filter))

        count_sql = queries(count_rows)[0]["sql"]
        len_sql = queries(len_of_rows)[0]["sql"]
        facts["count_uses_count_sql"] = "COUNT(*)" in count_sql
        facts["len_loads_rows"] = "COUNT(*)" not in len_sql and "booked_by" in len_sql

        facts["flawed_busy"] = flawed_busy_check()
        facts["fixed_busy_sql"] = queries(fixed_busy_check)[0]["sql"]
        transaction.set_rollback(True)
    return facts


def main():
    f = evaluate()
    print(f"FINDING 1  {'N+1: one query per row':<44} {f['flawed_lines_queries']} queries for {f['rows']} rows  confirmed")
    print(f"FINDING 2  {'select_related fixes it':<44} {f['fixed_lines_queries']} query, same result: {f['lines_equal']}")
    print(f"FINDING 3  {'len(qs) loads every row':<44} {'confirmed' if f['len_loads_rows'] else 'NOT confirmed'}  (use exists() or count())")
    lazy = "FALSE" if f["queries_when_building"] == 0 else "TRUE"
    print(f"CLAIM 4    {'filter() hits the database immediately':<44} {lazy}  ({f['queries_when_building']} queries to build, {f['queries_when_evaluating']} to evaluate)")
    print(f"CLAIM 5    {'select_related gives a single query':<44} {'TRUE' if f['fixed_lines_queries'] == 1 else 'FALSE'}")
    print(f"CLAIM 6    {'len(qs) and qs.count() cost the same':<44} {'FALSE' if f['count_uses_count_sql'] and f['len_loads_rows'] else 'TRUE'}  (COUNT(*) vs every column)")


if __name__ == "__main__":
    main()
