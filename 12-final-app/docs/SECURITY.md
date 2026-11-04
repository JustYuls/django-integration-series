# Campus Booking Hub: security notes

A short checklist of what this app does, why, and how to check it. Every item has a test.

## 1. Authentication (who are you?)

- Django's built-in login and logout (`/accounts/login/`, `/accounts/logout/`) and a sign-up page.
- Logout is a **POST** with a CSRF token. A plain link cannot log you out.
- Passwords are stored as **salted PBKDF2 hashes**. They are never stored as typed, and Django never shows them back.
- Weak passwords are rejected: too short, too common, all digits, or too similar to the username.

## 2. Authorization (what may you do?)

Two roles, defined in `accounts/roles.py` and created after every `migrate`:

| Role | Can do |
|---|---|
| Student | view, add, change, delete **their own** bookings |
| Staff | everything a Student can, plus manage every booking and manage rooms |

Rules:

- **Every sensitive view checks on the server.** Hiding a button is only convenience. The URL itself is protected.
- `login_required` answers "who are you?". It does not answer "is this yours?".
- Ownership is one rule in one place: `Booking.objects.visible_to(user)`. Views use it, so a student asking for someone else's booking gets a **404**, as if it did not exist.
- The owner is set by the service from `request.user`. The form has no owner field, so a posted `owner` is ignored.
- Rooms: anyone can read, only staff can create, change, or delete (`PermissionRequiredMixin`). Anonymous visitors are sent to the login page; logged-in users without permission get a **403**.

## 3. Data protection

- **CSRF:** every POST form has `{% csrf_token %}`. A POST without it is rejected with a 403.
- **XSS:** Django escapes template variables. We never use `|safe` on text a user typed.
- **SQL injection:** only the ORM is used. Values are sent as parameters.
- **E-mail privacy:** the room schedule shows who booked only to staff.

## 4. Secrets and configuration

- No secret is in the code. `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, mail passwords, and `DJANGO_DEBUG` are **environment variables**. See `.env.example`.
- With `DJANGO_DEBUG=0` the app **refuses to start** without `DJANGO_SECRET_KEY`.
- The real `.env` file is git-ignored. Only `.env.example` (no real values) is committed.
- If a secret ever reaches a repository, treat it as leaked: **rotate it**.

## 5. Production settings (when DEBUG is off)

`SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS` (one year), `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD`, and a real SMTP mailer.

Check with:

```bash
DJANGO_DEBUG=0 DJANGO_SECRET_KEY=... DJANGO_ALLOWED_HOSTS=campus.example.com EMAIL_HOST=smtp.example.com \
  python manage.py check --deploy --fail-level WARNING
```

In development (defaults) the same command reports 8 issues. In the production environment it reports none.

## 6. What `check --deploy` does NOT catch

- `ALLOWED_HOSTS = ["*"]` is accepted without a warning, but it switches Host header validation off.
- Missing ownership checks (broken access control). Only tests and review find those.
- Secrets committed to the repository.

## 7. Known limitations

- No rate limiting on login (add a package such as `django-axes`, or a gateway rule).
- No two-factor authentication, and no e-mail verification on sign-up.
- Existing bookings made before Part 11 have no owner, so only staff can see them.
