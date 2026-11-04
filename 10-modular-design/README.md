# Part 10: Design the Complete Application (LO 4.1)

The Campus Booking Hub is split into three focused apps with one-way dependencies, a service layer for workflows, namespaced URLs, and a written design with a decision log. A `design_review` package checks the architecture from the real imports, and verifies what an AI assistant said when reviewing the design.

This part starts Course Outcome 4.

## Course outcome

- **CO4:** Design, develop, secure, optimize, and present a complete Django-based integrated application, effectively leveraging Generative AI throughout to review, debug, optimize code, and justify design, security, and performance decisions based on best practices.
- **LO 4.1:** Design a full Django-based application with integrated modules, templates, models, and views.

## Read the design first

[docs/DESIGN.md](docs/DESIGN.md): requirements, data model, the three apps and their dependencies, how a request flows, and a decision log with the reasons.

## Set it up

Use the virtual environment from Part 4, then:

```bash
cd 10-modular-design
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

This part regenerates the migrations (`rooms` 0001, `bookings` 0001) because the models moved between apps and the learning database is throwaway. On a database with real data you would plan the move, for example with `SeparateDatabaseAndState`. Delete `db.sqlite3` if you carry one over from an earlier part.

## Test it

```bash
python manage.py test           # 54 tests
```

## The AI design review

```bash
python -m design_review.review
```

```
App dependency graph (built from the real imports):
  rooms        -> (nothing)
  bookings     -> holiday_api, rooms
  holiday_api  -> (nothing)
FINDING 1  one-way dependency: bookings -> rooms                confirmed
FINDING 2  the workflow lives in services.py, not in views      confirmed
FINDING 3  holiday_api is self-contained                        confirmed
CLAIM 4    there is a circular import between rooms and bookings FALSE  (no cycle found)
CLAIM 5    the rooms app imports the bookings app               FALSE
CLAIM 6    a cycle would be detected by our checker             TRUE  (bookings -> rooms -> bookings)
```

The AI answer used in the video was generated with Claude (Anthropic), shortened, and verified with this code.

## What is in the folder

| Path | What it is |
|---|---|
| `rooms/` | `Room` model, generic CRUD views, templates. Depends on nothing |
| `bookings/` | `Booking` model, form, `services.py`, views, notifications. Depends on `rooms` and `holiday_api` |
| `holiday_api/` | the holidays client (timeout, cache, one custom error), a page, a command. Depends on nothing |
| `campus_hub/` | settings, the project's `urls.py` (includes each app with a prefix), the home page |
| `templates/` | shared base layout and partials |
| `design_review/` | the import-graph checker, the AI review verification, 7 tests |
| `docs/DESIGN.md` | the written design and decision log |

## Tests (54)

| Group | Count |
|---|---|
| `campus_hub/tests.py`: project and design | 11 |
| `rooms/tests.py`: CRUD and PROTECT | 9 |
| `bookings/tests.py`: model, form, service, views | 17 |
| `holiday_api/tests.py`: client, page, command (all mocked) | 10 |
| `design_review/tests.py`: the architecture rules | 7 |

## Practice

1. Make `rooms` import `bookings` on purpose. Which test fails, and what does the message tell you?
2. Add a fourth app, `reports`, that lists bookings per room. Which dependencies are allowed? Update `ALLOWED` in `design_review/check_imports.py`.
3. Write a new entry for the decision log: why `booked_by` becomes a `User` in Part 11.
