# Final presentation script (about 8 minutes)

Run `python manage.py migrate` and `python manage.py seed_demo` first. Note the two printed passwords; they are random and shown once.

| Min | Show | Say |
|---|---|---|
| 0:00 | Home page | The problem: students double-book rooms. The Campus Booking Hub fixes it. |
| 1:00 | `rooms/`, then sign in as `demo_staff` | Public can read rooms; only staff change them (permissions). |
| 2:00 | Sign in as `demo_student`, make a booking | The server sets the owner; the form cannot. |
| 3:00 | Open another person's booking URL | 404: ownership is enforced on the server. |
| 3:30 | **Find a room** | One query with `Exists()`; back-to-back bookings do not clash. |
| 4:30 | Holiday notice | External API with a cache and a timeout; the site works when it is down. |
| 5:15 | Terminal: `python -m final_review.review` | A bug report, reproduced, then fixed; two false AI claims caught. |
| 6:15 | Terminal: `python -m final_review.perf` | Measure, then add one index. |
| 7:00 | Terminal: `python manage.py test` | 98 tests. |
| 7:30 | `docs/DECISIONS.md` | Every decision has a reason and evidence. |

Generative AI: say where you used it, what it got wrong, and how a test or script proved it.
