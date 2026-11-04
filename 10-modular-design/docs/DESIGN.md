# Campus Booking Hub: design

This document is the plan behind the code in this folder. It is short on purpose: the code and the tests are the details.

## 1. Requirements

Who uses the app, and what they need:

| Role | Needs |
|---|---|
| Student | See rooms, book a room, change or cancel their own booking, get a confirmation e-mail |
| Staff | Everything a student can do, plus manage rooms |
| Admin | Everything, plus the admin site |

Roles, login and permissions are built in Part 11. In this part the pages are open, so we can design the modules first.

Rules the app must enforce:

- A booking must end after it starts, and must not start in the past.
- A room cannot hold more people than its capacity.
- A room cannot be double booked.
- A booking cannot be made on a public holiday (when the holidays service answers).
- If the holidays service or the mail server fails, bookings still work.

## 2. Data model

```
Room 1 ----< Booking
 name (unique)      room (FK, PROTECT)
 capacity           booked_by, booker_email, purpose
 has_projector      attendees, start, end, created_at
```

`on_delete=PROTECT`: a room that has bookings cannot be deleted. History is never lost silently.

## 3. Modules (apps)

| App | Responsibility | Models | Depends on |
|---|---|---|---|
| `rooms` | the rooms people can book | `Room` | nothing |
| `bookings` | booking rules, forms, workflows, notifications | `Booking` | `rooms`, `holiday_api` |
| `holiday_api` | the client for the public holidays API | none | nothing |

```
bookings ---> rooms
    |
    +------> holiday_api
```

Dependencies point one way and nothing is circular. `design_review/check_imports.py` checks this from the real imports, and its tests fail if the rule is broken.

## 4. How a request flows (Model-View-Template across apps)

`POST /bookings/new/`

1. `campus_hub/urls.py` sends `bookings/...` to the `bookings` app (namespace `bookings`).
2. `bookings.views.booking_create` builds a `BookingForm` and validates it (fields, rooms, capacity, holiday, double booking).
3. If valid, the view calls `bookings.services.book_room(form)`: save the booking, then send the e-mail. A mail error is logged, never raised.
4. The view adds a message and redirects (Post, Redirect, Get). The list page shows the booking, with its room joined in one query.

The view only reads the request and calls the service. The workflow lives in the service, so it can be tested without HTTP.

## 5. Decision log

| # | Decision | Why | Alternatives rejected |
|---|---|---|---|
| 1 | Three apps: rooms, bookings, holiday_api | One responsibility each; `rooms` and `holiday_api` can be reused | One big app (everything coupled); one app per model (too many) |
| 2 | Dependencies point one way: bookings to rooms | No circular imports; `rooms` stays simple | `rooms` showing booking counts (it would depend on `bookings`) |
| 3 | A service layer (`services.py`) for workflows | Thin views; workflows testable without HTTP | Logic inside views; Django signals (hidden control flow) |
| 4 | `PROTECT` on `Booking.room` | Deleting a room must never silently delete booking history | `CASCADE` (what Part 8 used, with a warning page) |
| 5 | The holidays client is isolated, with timeout, cache, and one custom error | An outside service must never take our pages down | Calling `requests` from the form directly |
| 6 | Settings flag `HOLIDAYS_ENABLED`, off while testing | No test calls the real network | Mocking in every single test |
| 7 | Each app owns its URLs and a namespace | Names cannot clash; prefixes can change in one place | One big `urls.py` with typed paths |

## 6. Plan for Parts 11 and 12

- Security (Part 11): users and roles, permissions, owner-only edits, secrets in environment variables, HTTPS settings, `check --deploy` with zero issues.
- Performance and quality (Part 12): an index on `(room, start)`, a measured speedup, a debugging session, and the final demo.

## 7. Known limitations

- `booked_by` is plain text until Part 11 replaces it with a real user.
- The overlap check is a query, not a database constraint. Two requests at the very same moment could both pass it. SQLite cannot express an exclusion constraint; PostgreSQL can.
- The holiday check uses one country (`HOLIDAY_COUNTRY`).
