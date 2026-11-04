# Part 7: Templates, Models, and Forms (LO 3.1)

The Campus Booking Hub now stores data. `Room` and `Booking` are real models with a migration, the pages render live data with the template language, and a `ModelForm` accepts new bookings with layered validation. A small `form_review` package verifies what an AI assistant said about a deliberately flawed, AI-style form draft.

This part starts Course Outcome 3.

## Course outcome

- **CO3:** Develop dynamic, data-driven Django applications by implementing templates, models, database integration, CRUD operations, and API consumption, while using Generative AI to validate logic, improve data handling, and enhance integration workflows.
- **LO 3.1:** Implement Django templates, models, and forms to create dynamic web pages.

## Set it up

Use the virtual environment from Part 4 (see [04-first-project](../04-first-project/README.md)), then:

```bash
cd 07-templates-models-forms
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser     # optional: to add rooms in /admin
python manage.py runserver
```

Add a few rooms in `/admin/`, then try `/rooms/`, `/rooms/1/`, `/bookings/` and `/bookings/new/`.

## Test it

```bash
python manage.py test           # 39 tests
```

## The AI form review

`form_review/flawed.py` is a deliberately flawed, AI-style draft (never used by the real project). `form_review/review.py` checks every statement an AI assistant made about it. It runs inside a transaction that is rolled back, so it leaves no data:

```bash
python -m form_review.review
```

```
FINDING 1  No {% csrf_token %}: POST gets 403             confirmed  (403)
FINDING 2  |safe on user text lets a script through       confirmed
FINDING 3  No clean(): capacity and clashes unchecked     confirmed
CLAIM 4    a ModelForm checks capacity and clashes        FALSE
CLAIM 5    csrf_token is only for login forms             FALSE
CLAIM 6    {{ variables }} are escaped by default         TRUE
```

(The line `Forbidden (CSRF cookie not set.)` printed above the results is Django logging the expected 403.) The AI answer used in the video was generated with Claude (Anthropic), shortened, and verified with this code.

## What is in the folder

| Path | What it is |
|---|---|
| `bookings/models.py` | `Room` and `Booking`, with `ForeignKey`, `Meta.ordering`, and a model-level `clean()` |
| `bookings/migrations/0001_initial.py` | the migration created by `makemigrations` |
| `bookings/admin.py` | both models registered in the admin |
| `bookings/forms.py` | `BookingForm`: widgets, and `clean()` for past start, capacity, and double bookings |
| `bookings/views.py` | list, detail, and the form view (GET, POST, redirect) |
| `bookings/templates/bookings/` | `rooms.html`, `room_detail.html`, `booking_list.html`, `booking_form.html` |
| `form_review/` | the flawed draft, the verification script and its 7 tests |

## Tests (39)

| Group | Count | What it covers |
|---|---|---|
| `campus_hub/tests.py` | 6 | check, default apps, SQLite, time zone, migrations, admin login |
| `bookings/tests.py` | 26 | models, form validation rules, views, the 403 without a CSRF token, escaping, filters, empty states, routes, admin |
| `form_review/tests.py` | 7 | the 3 findings confirmed, claims 4 and 5 shown false, claim 6 shown true |

## Notes

- `|safe` turns auto-escaping off. Never use it on text a user typed.
- Validation layers: field rules, `clean_<field>()`, the form's `clean()`, and the model's `clean()`.
- `Booking.objects.filter(...)` in the double-booking check is a preview. Queries are the subject of Part 8.
- `booked_by` is plain text for now. It becomes a real user in Part 11.

## Practice

1. Add a rule: a booking may not be longer than 4 hours. Where does it go, and what test proves it?
2. Remove `{% csrf_token %}` from `booking_form.html` and submit the form in a browser. What do you see?
3. Add `phone = models.CharField(max_length=20, blank=True)` to `Booking`. What do you have to run, and why?
