"""Part 12: measure before you optimize. Count queries, time them, and read the query plan.

Run from the project folder (after migrate):   python -m final_review.perf [rows]
"""
import os
import random
import sys
import time
from datetime import timedelta

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_hub.settings")
django.setup()

from django.db import connection, transaction  # noqa: E402
from django.test.utils import CaptureQueriesContext  # noqa: E402
from django.utils import timezone  # noqa: E402

from bookings.availability import available_rooms  # noqa: E402
from bookings.models import Booking  # noqa: E402
from rooms.models import Room  # noqa: E402

INDEX_NAME = "booking_room_start_end_idx"


def naive_available_rooms(start, end):
    """The first idea: ask the database once per room (N+1)."""
    return [r for r in Room.objects.all() if not Booking.objects.filter(room=r, start__lt=end, end__gt=start).exists()]


def milliseconds(call, repeats):
    began = time.perf_counter()
    for _ in range(repeats):
        call()
    return (time.perf_counter() - began) / repeats * 1000


def plan_of(queryset):
    sql, params = queryset.query.sql_with_params()
    with connection.cursor() as cursor:
        cursor.execute("EXPLAIN QUERY PLAN " + sql, params)
        return [row[3] for row in cursor.fetchall()]


def measure(rows=20000, rooms=40, repeats=10):
    """Fill the tables inside a transaction, measure, and roll everything back (the index too)."""
    random.seed(7)
    facts = {"rows": rows}
    with transaction.atomic():
        room_list = [Room.objects.create(name=f"Perf {i}", capacity=40) for i in range(rooms)]
        base = timezone.now()
        bookings = []
        for _ in range(rows):
            start = base + timedelta(hours=random.randint(-4000, 4000))
            bookings.append(Booking(room=random.choice(room_list), booked_by="perf", start=start, end=start + timedelta(hours=1)))
        Booking.objects.bulk_create(bookings, batch_size=5000)
        start, end = base + timedelta(days=3), base + timedelta(days=3, hours=2)
        facts["rooms"] = Room.objects.count()

        with CaptureQueriesContext(connection) as ctx:
            naive = naive_available_rooms(start, end)
        facts["naive_queries"] = len(ctx)
        with CaptureQueriesContext(connection) as ctx:
            single = list(available_rooms(start, end))
        facts["single_queries"] = len(ctx)
        facts["same_answer"] = sorted(r.pk for r in naive) == sorted(r.pk for r in single)
        facts["naive_ms"] = milliseconds(lambda: naive_available_rooms(start, end), repeats)

        with connection.cursor() as cursor:
            cursor.execute(f"DROP INDEX IF EXISTS {INDEX_NAME}")  # SQLite DDL is transactional: the rollback restores it
        facts["plan_without_index"] = plan_of(available_rooms(start, end))
        facts["single_ms_without_index"] = milliseconds(lambda: list(available_rooms(start, end)), repeats)
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE INDEX {INDEX_NAME} ON bookings_booking (room_id, start, end)")
            cursor.execute("ANALYZE")
        facts["plan_with_index"] = plan_of(available_rooms(start, end))
        facts["single_ms_with_index"] = milliseconds(lambda: list(available_rooms(start, end)), repeats)
        transaction.set_rollback(True)
    return facts


def main():
    rows = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    f = measure(rows=rows)
    print(f"{f['rows']:,} bookings, {f['rooms']} rooms, one 2-hour window")
    print(f"1. ask once per room (N+1): {f['naive_queries']:>2} queries  {f['naive_ms']:>7.1f} ms")
    print(f"2. one query with EXISTS  : {f['single_queries']:>2} query    {f['single_ms_without_index']:>7.1f} ms   same answer: {f['same_answer']}")
    print(f"   plan: {f['plan_without_index'][-1]}")
    print(f"3. + index (room, start, end): {f['single_ms_with_index']:>7.1f} ms   ({f['single_ms_without_index'] / f['single_ms_with_index']:.0f}x faster)")
    print(f"   plan: {f['plan_with_index'][-1]}")


if __name__ == "__main__":
    main()
