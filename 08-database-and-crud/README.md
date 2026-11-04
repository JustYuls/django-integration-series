# Part 8: Database and CRUD (LO 3.2)

The Campus Booking Hub gets full create, read, update, and delete pages for rooms and bookings. You work with the ORM: QuerySets and filters, lazy evaluation, `select_related` to avoid the N+1 problem, and a double-booking check that excludes the booking being edited. An `orm_review` package verifies what an AI assistant said about a deliberately flawed query draft.

## Course outcome

- **CO3:** Develop dynamic, data-driven Django applications by implementing templates, models, database integration, CRUD operations, and API consumption, while using Generative AI to validate logic, improve data handling, and enhance integration workflows.
- **LO 3.2:** Connect Django applications to databases and perform CRUD operations.

## Set it up

Use the virtual environment from Part 4, then:

```bash
cd 08-database-and-crud
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser     # optional
python manage.py runserver
```

Try `/rooms/`, `/rooms/new/`, `/bookings/`, and `/bookings/new/`.

## Test it

```bash
python manage.py test           # 51 tests
```

## The AI query review

```bash
python -m orm_review.review
```

```
FINDING 1  N+1: one query per row                       11 queries for 10 rows  confirmed
FINDING 2  select_related fixes it                      1 query, same result: True
FINDING 3  len(qs) loads every row                      confirmed  (use exists() or count())
CLAIM 4    filter() hits the database immediately       FALSE  (0 queries to build, 1 to evaluate)
CLAIM 5    select_related gives a single query          TRUE
CLAIM 6    len(qs) and qs.count() cost the same         FALSE  (COUNT(*) vs every column)
```

The AI answer used in the video was generated with Claude (Anthropic), shortened, and verified with this code. The review runs in a transaction that is rolled back.

## What is in the folder

| Path | What it is |
|---|---|
| `bookings/views.py` | class-based create, update, and delete views for rooms; function views for bookings |
| `bookings/forms.py` | `BookingForm`; editing excludes the booking itself from the clash check |
| `bookings/templates/bookings/` | list, form, and confirm-delete templates |
| `bookings/tests.py` | model, form, view, and query-count tests |
| `orm_review/` | the flawed query draft, the verification script, and its tests |

## Practice

1. Write a test with `assertNumQueries` for `/bookings/`. How many queries run with and without `select_related("room")`?
2. Edit a booking without changing its times. Why must the clash check exclude the booking itself?
3. Replace `qs.exists()` with `len(qs) > 0` in a test and compare the query SQL. What changed?
