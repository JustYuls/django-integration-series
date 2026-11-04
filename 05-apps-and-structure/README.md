# Part 5: Apps, Templates, Static Files, and an AI Structure Review (LO 2.2 and 2.4)

The Campus Booking Hub from Part 4, now organized: a `bookings` app, shared templates with a base layout and partials, static files, and a small `ai_review` package that checks what an AI assistant said about a deliberately flawed copy of the settings.

## Course outcome

- **CO2:** Set up and configure a Django project and applications, and use Generative AI to assist in designing, reviewing, and troubleshooting Django project structures, views, and URL routing.
- **LO 2.2:** Create and organize Django apps, project folders, and templates.
- **LO 2.4:** Use Generative AI to review project structure, detect configuration issues, and suggest improvements.

## Set it up

Use the virtual environment from Part 4 (see [04-first-project](../04-first-project/README.md)), then:

```bash
cd 05-apps-and-structure
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver      # http://127.0.0.1:8000/  and  /rooms/
```

## Test it

```bash
python manage.py test           # 21 tests
```

## The AI structure review

`ai_review/flawed.py` builds five planted problems (only inside the review, never in the real settings). `ai_review/review.py` checks every statement an AI assistant made about them:

```bash
python -m ai_review.review
```

```
ISSUE 1  App 'bookings' is not registered         confirmed      manage.py check: missed
ISSUE 2  Template folder typo ('template')        confirmed      manage.py check: missed
ISSUE 3  STATICFILES_DIRS folder is missing       confirmed      manage.py check: FOUND (staticfiles.W004)
ISSUE 4  {% static %} without {% load static %}   confirmed      manage.py check: missed
ISSUE 5  DEBUG on, ALLOWED_HOSTS empty            confirmed      manage.py check: missed (only check --deploy)
CLAIM 6  check flags all five                     FALSE  (found 1 of 5)
CLAIM 7  DEBUG = False fixes the template         FALSE  (TemplateDoesNotExist remains)
```

The AI answer used in the video was generated with Claude (Anthropic), shortened, and verified with this code. Lesson: `manage.py check` is necessary but not sufficient, and a confident AI answer still needs a test.

## What is in the folder

| Path | What it is |
|---|---|
| `bookings/` | the first app, created with `startapp` and registered in `INSTALLED_APPS` |
| `bookings/templates/bookings/rooms.html` | an app template, namespaced with the app name |
| `templates/base.html` | the page skeleton with blocks, the static tag and two includes |
| `templates/partials/` | `_navbar.html` and `_footer.html`, reusable pieces |
| `templates/home.html` | a page that extends the base |
| `static/css/site.css` | a shared style sheet, found through `STATICFILES_DIRS` |
| `campus_hub/urls.py` | two `TemplateView` routes (real views come in Part 6) |
| `ai_review/` | the planted problems, the verification script and its 7 tests |

## Tests (21)

| Group | Count | What it covers |
|---|---|---|
| `campus_hub/tests.py` | 6 | check, default apps, SQLite, time zone, migrations, admin login |
| `bookings/tests.py` | 8 | app registered, pages load, base and partials used, app template, static file, two common mistakes |
| `ai_review/tests.py` | 7 | the 5 findings confirmed and the 2 claims shown false |

## Practice

1. Add a second app called `accounts` and register it. Which tests change?
2. Put a typo in the `DIRS` setting and read the Django debug page. Where did Django look?
3. Write a sixth planted problem and check it with `manage.py check` and with a test.
