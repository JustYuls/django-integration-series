# Part 12: Debugging, Optimizing, and Presenting the Final Application (LO 4.3)

The finale. The Campus Booking Hub gets a "Find a room" page, a bug report is reproduced and fixed, a slow query is measured and sped up with one index, and the whole project is presented with its decisions written down.

## Course outcome

- **CO4:** Design, develop, secure, optimize, and present a complete Django-based integrated application, effectively leveraging Generative AI throughout to review, debug, optimize code, and justify design, security, and performance decisions based on best practices.
- **LO 4.3:** Debug and refine code using AI-assisted suggestions and code reviews.

## Set it up

Use the virtual environment from Part 4, then:

```bash
cd 12-final-app
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo      # 3 rooms, demo_student, demo_staff (random passwords, printed once)
python manage.py runserver
```

Open `/bookings/find-room/` (login needed) to search for a free room.

## Test it

```bash
python manage.py test           # 98 tests
```

## The debugging review

```bash
python -m final_review.review
```

```
Bug report: 'Lab C is shown as busy 10:00-12:00, but it has no booking then.'
  buggy query, 10:00-12:00 -> Open Studio
  fixed query, 10:00-12:00 -> Lab C, Open Studio
FINDING 1  the bug is reproduced: Lab C is wrongly excluded      confirmed
FINDING 2  the SQL has two separate EXISTS, the fix has one       confirmed
FINDING 3  the fix (one EXISTS) is one query, and correct          confirmed
CLAIM 4    the boundary uses <= so back-to-back bookings clash     FALSE  (Room A is free at 11:00)
CLAIM 5    select_related() fixes it                                FALSE  (same wrong answer)
CLAIM 6    one EXISTS subquery fixes it                             TRUE
```

The AI answer used in the video was written with Claude (Anthropic), shortened, and verified with this code. The review runs inside a transaction that is rolled back, so it never changes your data.

## The performance measurement

```bash
python -m final_review.perf 100000
```

```
100,000 bookings, 43 rooms, one 2-hour window
1. ask once per room (N+1): 44 queries     26.5 ms
2. one query with EXISTS  :  1 query      165.2 ms   same answer: True
   plan: SEARCH U0 USING INDEX bookings_booking_room_id_6f0fa517 (room_id=?)
3. + index (room, start, end):     8.3 ms   (20x faster)
   plan: SEARCH U0 USING COVERING INDEX booking_room_start_end_idx (room_id=? AND start<?)
```

Times differ on every machine; the order does not. Fewer queries is not automatically faster: measure first.

## What is in the folder

| Path | What it is |
|---|---|
| `bookings/availability.py` | `available_rooms(start, end, attendees)`: one `Exists()` query |
| `bookings/models.py` | the composite index `booking_room_start_end_idx` (migration `0003`) |
| `bookings/management/commands/seed_demo.py` | demo data with random passwords; safe to run again |
| `final_review/` | the buggy version, the debugging review, the performance measurement, 8 tests |
| `docs/DECISIONS.md` | every design, security, and performance decision, with its evidence |
| `docs/PRESENTATION.md` | an 8-minute demo script |
| `docs/SECURITY.md` | security notes from Part 11 |

## Tests (98)

| Group | Count |
|---|---|
| Project, routing, production settings | 15 |
| `accounts`: roles, sign-up, login, logout, CSRF | 14 |
| `rooms`: public reading, 403, staff CRUD | 8 |
| `bookings`: ownership, services, forms | 18 |
| `bookings/test_final.py`: availability, form, find-room page, index, demo data | 19 |
| `holiday_api`: client, page, command (mocked) | 10 |
| `security_review` | 6 |
| `final_review`: debugging and performance review | 8 |

## Practice

1. In `buggy.py`, what does the generated SQL look like? Why are there two `EXISTS`?
2. Drop the index inside `perf.py` and compare the plans. Which word in the plan tells you the index covers the query?
3. Write your own `docs/DECISIONS.md` entry for one choice in your project. What is the evidence?
