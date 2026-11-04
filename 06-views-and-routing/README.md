# Part 6: Views and URL Routing (LO 2.3)

The Campus Booking Hub gets real views and a clean routing table: function-based and class-based views, `path()` converters, `re_path()`, `include()`, named and namespaced routes, `reverse()` and the `{% url %}` tag. A small `routing_review` package verifies what an AI assistant said when troubleshooting a flawed copy of the routes.

This is the last part of Course Outcome 2.

## Course outcome

- **CO2:** Set up and configure a Django project and applications, and use Generative AI to assist in designing, reviewing, and troubleshooting Django project structures, views, and URL routing.
- **LO 2.3:** Design and implement views, URL patterns, and routing logic.

## Set it up

Use the virtual environment from Part 4 (see [04-first-project](../04-first-project/README.md)), then:

```bash
cd 06-views-and-routing
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Try these addresses: `/`, `/rooms/`, `/rooms/2/`, `/rooms/abc/` (404), `/room-2/` (the old link style), `/calendar/2027/4/`, `/calendar/2027/13/` (404).

## Test it

```bash
python manage.py test           # 30 tests
```

## The AI routing review

`routing_review/flawed_urls.py` and `flawed_app_urls.py` are deliberately flawed copies of the routes (never used by the real project). `routing_review/review.py` checks every statement an AI assistant made about them:

```bash
python -m routing_review.review
```

```
FINDING 1  No app_name: bookings:... cannot reverse         confirmed
FINDING 2  <str:page>/ shadows /rooms/ (order matters)      confirmed
FINDING 3  re_path without ^ and $ matches too much         confirmed
CLAIM 4    most specific route wins, whatever the order     FALSE
CLAIM 5    re_path is anchored automatically                FALSE
CLAIM 6    include + app_name gives namespaced names        TRUE  (reverse -> /rooms/)
```

The AI answer used in the video was generated with Claude (Anthropic), shortened, and verified with this code. Django uses the **first** matching route, and `re_path()` is **not** anchored for you.

## What is in the folder

| Path | What it is |
|---|---|
| `bookings/views.py` | function-based views (`home`, `room_detail`, `calendar`) and a class-based view (`RoomListView`) |
| `bookings/urls.py` | the app's routes: `app_name`, `<int:...>` converters, a `re_path()` for old links |
| `campus_hub/urls.py` | the project's table of contents: the admin, the home page, and `include("bookings.urls")` |
| `bookings/data.py` | sample rooms (Part 7 replaces them with a model) |
| `templates/partials/_navbar.html` | links built with `{% url %}`, never typed |
| `routing_review/` | the flawed routes, the verification script and its 7 tests |

## Tests (30)

| Group | Count | What it covers |
|---|---|---|
| `campus_hub/tests.py` | 6 | check, default apps, SQLite, time zone, migrations, admin login |
| `bookings/tests.py` | 17 | function and class views, 404 and 405, converters, `re_path()`, `resolve()`, `reverse()`, namespaces, the navbar |
| `routing_review/tests.py` | 7 | the 3 findings confirmed, claims 4 and 5 shown false, claim 6 shown true |

## Notes

- Our tests show a `POST` to `/rooms/1/` gives **405**. On the running server, a `POST` without a CSRF token gets **403** first. Forms and CSRF come in Parts 7 and 11.
- `re_path()` passes captured values as text, so `room_detail` converts with `int(room_id)`. `path()` with `<int:room_id>` already passes an integer.

## Practice

1. Add `path("rooms/<int:room_id>/edit/", ...)` before and after the detail route. Does the order matter here?
2. Put a prefix on the include: `path("api/", include("bookings.urls"))`. What do the addresses become? Do the `{% url %}` links still work?
3. Write a fourth routing bug and a test that proves it.
