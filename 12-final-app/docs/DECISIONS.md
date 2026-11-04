# Decisions: Campus Booking Hub

Every choice below has a reason and a test or a measurement behind it (CO4: justify design, security, and performance decisions).

## Design

| Decision | Why | Evidence |
|---|---|---|
| Three apps: `rooms`, `bookings`, `holiday_api` | Each has one job; `bookings` may import `rooms`, never the other way | `design_review/check_imports.py` (Part 10) |
| A service layer (`bookings/services.py`) | Views stay thin; rules live in one testable place | `bookings/tests` |
| External API behind one client with a cache and a timeout | A slow or broken service must not break booking | `holiday_api` tests (mocked) |
| Availability in its own module (`bookings/availability.py`) | One function, one query, easy to test and to reuse | `test_final.py` |

## Security

| Decision | Why | Evidence |
|---|---|---|
| Roles are groups of permissions (Student, Staff) | People get a role, not a list | `accounts/roles.py`, tests |
| Ownership rule in `Booking.objects.visible_to(user)` | One rule, used by every view; other people's bookings give 404 | `bookings` tests |
| The server sets the owner, never the form | Prevents mass assignment | `services.book_room` tests |
| Secrets from environment variables; no key means no start in production | A loud failure beats a quiet vulnerability | `check --deploy`: 8 issues, then none |
| `seed_demo` prints random passwords once | No default password in the repository | `SeedDemoTests` |

Known gaps (not done on purpose, see `docs/SECURITY.md`): login rate limiting, two-factor authentication, e-mail verification.

## Performance

The bug: "Lab C is shown as busy, but it has no booking then." Cause: `exclude(bookings__start__lt=end, bookings__end__gt=start)` on a multi-valued relation can match each condition with a different booking, so a room with an early and a late booking looked busy all day. Fix: one `Exists()` subquery, so both conditions apply to the same booking (`final_review/debug.py`).

Then we measured instead of guessing (`python -m final_review.perf 100000`, 100,000 bookings, 43 rooms, one 2-hour window; times vary by machine):

| Version | Queries | Time | Query plan |
|---|---|---|---|
| Ask once per room (N+1) | 44 | 26.5 ms | n/a |
| One `EXISTS` query | 1 | 165.2 ms | `SEARCH ... USING INDEX bookings_booking_room_id_...` |
| One `EXISTS` query + index `(room, start, end)` | 1 | 8.3 ms | `SEARCH ... USING COVERING INDEX booking_room_start_end_idx` |

Lessons:

1. Fewer queries is not automatically faster: the single query was slower than N+1 until it had a good index.
2. The index must match the query. An earlier experiment with an index on `(owner, start)` did not help (24 ms against 29 ms), so it was not kept.
3. The accepted index is declared in `Booking.Meta.indexes` and created by migration `0003`; a test checks that it exists.

## What we would do next

Rate-limit logins, add two-factor authentication for staff, paginate long booking lists, and move from SQLite to PostgreSQL before real use.
