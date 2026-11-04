# Part 4: Install and Start Your First Django Project (LO 2.1)

The first version of the **Campus Booking Hub**: a Django 6.1 project with a virtual environment, a configured database and time zone, the first migration, and tests. Later parts grow this project.

## Course outcome

- **CO2:** Set up and configure a Django project and applications, and use Generative AI to assist in designing, reviewing, and troubleshooting Django project structures, views, and URL routing.
- **LO 2.1:** Install, configure, and initialize Django projects and applications.

## Set it up

You need Python 3.12 or newer. Run these from the repository root.

Windows (PowerShell):

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
cd 04-first-project
pip install -r requirements.txt
```

Mac or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
cd 04-first-project
pip install -r requirements.txt
```

## Run it

```bash
python manage.py migrate        # creates db.sqlite3 with Django's built-in tables
python manage.py runserver      # http://127.0.0.1:8000/  shows the welcome page
```

Other commands from the video:

```bash
python manage.py check                # validate the project
python manage.py check --deploy       # a to-do list for Part 11 (8 issues for now)
python manage.py diffsettings         # settings that differ from Django's defaults
```

## Test it

```bash
python manage.py test           # 8 tests
```

## What is in the folder

| Path | What it is |
|---|---|
| `manage.py` | the command-line tool for this project |
| `campus_hub/settings.py` | every setting. Changed from the default: `TIME_ZONE = 'Asia/Manila'` |
| `campus_hub/urls.py` | one route so far: the admin site |
| `campus_hub/wsgi.py`, `asgi.py` | entry points for production servers |
| `campus_hub/tests.py` | 8 tests: system check, apps, SQLite, time zone, migrations, welcome page, admin login, 404 |
| `requirements.txt` | pinned versions: Django 6.1.3 and its dependencies |

## Important notes

- `SECRET_KEY`, `DEBUG = True` and `ALLOWED_HOSTS = []` are Django's **development defaults**. The `django-insecure-` key is a throwaway. They are fixed in Part 11 when the app is secured.
- `db.sqlite3` is created by `migrate` and is not committed.
- The development server (`runserver`) is for learning only. Never use it in production.

## Practice

1. Change `TIME_ZONE` to your own time zone and run `python manage.py test`. What fails, and why?
2. Run `python manage.py help` and read the list of commands.
3. Remove `db.sqlite3`, run `runserver`, and read the warning. Then run `migrate`.
