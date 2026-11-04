# Part 11: Authentication, Permissions, and Security (LO 4.2)

The Campus Booking Hub gets users, roles, and real access control: login and sign-up, Student and Staff groups, permissions on rooms, owner-only bookings, secrets in environment variables, production hardening, and a `check --deploy` that reports no issues. A `security_review` package verifies what an AI assistant said when reviewing a flawed security draft.

## Course outcome

- **CO4:** Design, develop, secure, optimize, and present a complete Django-based integrated application, effectively leveraging Generative AI throughout to review, debug, optimize code, and justify design, security, and performance decisions based on best practices.
- **LO 4.2:** Implement security measures including authentication, authorization, and data protection.

Read [docs/SECURITY.md](docs/SECURITY.md) for the checklist.

## Set it up

Use the virtual environment from Part 4, then:

```bash
cd 11-security
pip install -r requirements.txt
python manage.py migrate            # also creates the Student and Staff roles
python manage.py createsuperuser    # optional
python manage.py runserver
```

Sign up at `/accounts/signup/` (you become a Student). To make someone Staff, add them to the **Staff** group in `/admin/`.

## Secrets and production settings

Real values come from environment variables, never from code. Copy `.env.example` to `.env` (git-ignored) and load it with your shell or host. The production check:

```bash
# Windows PowerShell
$env:DJANGO_DEBUG="0"; $env:DJANGO_SECRET_KEY="<a long random value>"; $env:DJANGO_ALLOWED_HOSTS="campus.example.com"; $env:EMAIL_HOST="smtp.example.com"
python manage.py check --deploy --fail-level WARNING
```

```
System check identified no issues (0 silenced).
```

With the development defaults, `check --deploy` reports 8 issues. With `DJANGO_DEBUG=0` and no `DJANGO_SECRET_KEY`, the app refuses to start.

## Test it

```bash
python manage.py test           # 71 tests (some start a separate process to check production settings)
```

## The AI security review

```bash
python -m security_review.review
```

```
FINDING 1  login_required alone lets Alice cancel Bobs booking      confirmed
FINDING 2  the real view answers 404 for a booking you do not own   confirmed
FINDING 3  ALLOWED_HOSTS=[*] accepts any Host; check --deploy is silent confirmed
CLAIM 4    login_required is enough to protect a booking            FALSE
CLAIM 5    hiding the Cancel button prevents unauthorized cancels   FALSE
CLAIM 6    Django stores passwords as salted hashes by default      TRUE  (pbkdf2_sha256)
```

The AI answer used in the video was generated with Claude (Anthropic), shortened, and verified with this code. The log lines printed above the results are Django logging the expected 404 and rejected host.

## What is in the folder

| Path | What it is |
|---|---|
| `accounts/` | sign-up, login and logout wiring, and `roles.py` (Student and Staff groups with their permissions) |
| `bookings/` | `Booking.owner`, a custom permission, `visible_to(user)`, services that set the owner, and views that check access |
| `rooms/` | public reading, staff-only management with `PermissionRequiredMixin` |
| `campus_hub/settings.py` | secrets and hosts from the environment, production hardening, SMTP mailer |
| `.env.example` | the list of environment variables, with no real values |
| `security_review/` | the flawed draft, the verification script, 6 tests |
| `docs/SECURITY.md` | what is protected, how, and what `check --deploy` does not catch |

## Tests (71)

| Group | Count |
|---|---|
| `campus_hub/tests.py`: project, routing, production settings | 15 |
| `accounts/tests.py`: roles, sign-up, login, logout, CSRF | 14 |
| `rooms/tests.py`: public reading, 403 and redirects, staff CRUD | 8 |
| `bookings/tests.py`: ownership, 404 for others, staff, services, forms | 18 |
| `holiday_api/tests.py`: client, page, command (mocked) | 10 |
| `security_review/tests.py`: the AI review | 6 |

## Notes

- During tests a fast password hasher is used, so the suite stays quick. A test switches back to Django's real default to prove passwords are PBKDF2 hashes.
- Bookings made before this part have no owner, so only staff can see them.

## Practice

1. Log in as a Student and open another student's `/bookings/<id>/edit/`. What do you get, and why not a 403?
2. Remove `{% csrf_token %}` from the login template. What happens, and which test would catch it?
3. Set `ALLOWED_HOSTS = ["*"]` and run `check --deploy` with the production environment. What does the check say?
