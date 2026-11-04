# Integrative Programming with Django: From Scripts to a Secure App

**Plan v1: for your review. Nothing is recorded or uploaded yet.**
Built from the syllabus CSIPT101 Integrative Programming Technologies 1 (BSIT), same pattern as the EF Core series.

## Proposed decisions (please confirm or change)

| Item | Proposal |
|---|---|
| Length | **12 parts**, 3 parts for each Course Outcome (CO1 to CO4). Parts 1 to 3 run 6 to 7 min. **Parts 4 to 12 run up to about 10 min** (updated on request) for deeper discussion of each topic |
| No "periods" | Videos never say Prelim, Midterm, Semi-final or Final, and never show grading. They are just Part 1 to Part 12. The CO/LO structure runs through them |
| Stack | Python 3.14 (installed on this PC), **Django 6.1** (latest, 6.1.3), `requests`, Django's built-in test runner. Versions pinned |
| Database | SQLite (PostgreSQL shown conceptually, as the syllabus lists both) |
| Running project | **Campus Booking Hub** (see below) |
| Viewer level | 3rd-year BSIT: knows basic Python (functions, classes, lists, dicts). New to Django, HTTP details and APIs |
| Format | Same as EF Core: slides plus real terminal output, male Piper voice (`en_US-ryan-high`), burned-in captions plus SRT, animated presenter **Sir Yuls** (lower-right, 300 px), numbered files, **PART N OF 12** thumbnails, YouTube kit, 1 to 2 Shorts per part |
| Series name / repo | "Integrative Programming with Django: From Scripts to a Secure App". Repo `django-integration-series` (JustYuls, public, MIT), local folder `D:\MIT\django-integration-series` |
| Branding | Small "CSIPT101" tag on the intro slide only. Tell me if you want it removed |
| Generative AI | Every CO has a Generative AI outcome, so each CO block includes an on-screen **AI check**: the prompt, the AI answer, and then **we verify it with real tools** (`manage.py check`, tests, docs). The AI answers shown are real responses, labeled as such, never presented as automatically correct |

## How every part covers the outcomes

Each part has the same outcome frame, so every CO and LO is spoken and shown:

1. **Opening card (first 15 seconds):** "Course Outcome 2: Set up and configure a Django project... This part covers LO 2.1: Install, configure and initialize Django projects."
2. **Narration** says the LO in plain words, then teaches it.
3. **Closing checklist:** the LO text with a tick, and "Next: LO 2.2".
4. Part 1 also gives a 60-second roadmap of all four COs.
5. The last part of each CO block ends with a **CO recap** card: "You can now ... (CO1)".

## Outcome coverage map

| Part | CO | LO covered | Title |
|---|---|---|---|
| 1 | CO1 | Course roadmap, 1.1 | Scripting Languages for Integration |
| 2 | CO1 | 1.2 | Client-Server and the HTTP Request Cycle |
| 3 | CO1 | 1.3 + CO1 GenAI | Choosing the Right API and Language (with AI) |
| 4 | CO2 | 2.1 | Install and Start Your First Django Project |
| 5 | CO2 | 2.2 + 2.4 | Apps, Templates, Static Files, and an AI Structure Review |
| 6 | CO2 | 2.3 | Views and URL Routing |
| 7 | CO3 | 3.1 | Templates, Models, and Forms |
| 8 | CO3 | 3.2 | Database and CRUD |
| 9 | CO3 | 3.3 + 3.4 | Consuming an External API, Validated with AI-Assisted Tests |
| 10 | CO4 | 4.1 | Design the Complete Application |
| 11 | CO4 | 4.2 | Authentication, Permissions, and Security |
| 12 | CO4 | 4.3 + CO4 present/justify | AI-Assisted Debugging, Optimization, and Final Presentation |

Every LO in the syllabus (1.1 to 4.3) is covered, plus the three Generative AI parts of CO1 to CO4 (CO1 comparison, CO2 review, CO3 validation, CO4 debug/justify). Orientation (course expectations) is the roadmap in Part 1.

## The running project: Campus Booking Hub

A Django app where students and staff book rooms and equipment.

| Piece | Used in |
|---|---|
| `Room`, `Equipment` models | Parts 7 to 8 |
| `Booking` (user, room, start/end, status) | Parts 7 to 10 |
| Public holidays check: external API **Nager.Date** (free, no key) so bookings on a Philippine holiday are flagged | Part 9 |
| Weather note for outdoor venues: **Open-Meteo** (free, no key), optional | Part 9 |
| Email notification on booking (console email backend) | Part 10 |
| Roles: Student, Staff, Admin; permissions, CSRF, password hashing | Part 11 |
| Parts 1 to 3 use small standalone scripts (Python and JS) that call the same public APIs, so the viewer sees scripting, HTTP, and APIs before Django | Parts 1 to 3 |

All API code runs against real calls in the recording, and the tests use mocks so they work offline.

## Part-by-part outline

Every part: goal, LO, what the viewer builds, key concepts, one common mistake, next part.

### CO1: Scripting and client-server (3 parts)

**Part 1: Scripting Languages for Integration** (LO 1.1)
- Programming vs scripting, Python vs JavaScript, syntax and basic constructs, automation and integration roles, real examples.
- Build: a Python script and a JS script that fetch the same holiday list and print it.
- Mistake: thinking "scripting" means "not real programming".
- Next: what happens between the script and the server.

**Part 2: Client-Server and the HTTP Request Cycle** (LO 1.2)
- Clients, servers, intermediaries, TCP/IP overview, HTTP/HTTPS, request-response lifecycle, status codes, cloud vs local servers.
- Build: a tiny Python server and a client, show the raw request and response, add a 404 and a 500.
- Mistake: ignoring status codes and trusting a 200.
- Next: choosing an API style.

**Part 3: Choosing the Right API and Language** (LO 1.3 + GenAI)
- REST vs SOAP, public, private, internal APIs, Python/JavaScript/PHP for APIs, a decision matrix.
- AI check: ask an AI assistant to compare options for a scenario, then **verify claims** against docs and a quick test.
- CO1 recap card.
- Mistake: picking by habit, not by requirement.
- Next: set up Django.

### CO2: Django setup, structure, routing (3 parts)

**Part 4: Install and Start Your First Django Project** (LO 2.1)
- Python install check, virtual environment, install Django, `startproject`, run the server, `settings.py` tour, migrations first run.
- Mistake: not using a virtual environment.

**Part 5: Apps, Templates, Static Files, and an AI Structure Review** (LO 2.2 + 2.4)
- `startapp`, `INSTALLED_APPS`, templates folder, static files, reusable components, modular layout.
- AI check: give an AI a deliberately flawed project (app not registered, wrong template path, DEBUG on); compare the AI's findings with `manage.py check`.
- Mistake: forgetting to register the app.

**Part 6: Views and URL Routing** (LO 2.3)
- Function-based vs class-based views, `path` vs `re_path`, namespaces, `include`, reverse URLs.
- Build: the Campus Booking Hub home, room list, and detail routes.
- CO2 recap card.
- Mistake: hard-coding URLs in templates.

### CO3: Data-driven apps and API consumption (3 parts)

**Part 7: Templates, Models, and Forms** (LO 3.1)
- Template inheritance, models, `ModelForm`, validation, rendering data dynamically.
- Mistake: validating only in JavaScript.

**Part 8: Database and CRUD** (LO 3.2)
- SQLite and PostgreSQL, ORM basics, QuerySets and filters, create/read/update/delete views, `select_related`.
- Mistake: running queries inside a loop (N+1).

**Part 9: Consuming an External API, Validated with AI-Assisted Tests** (LO 3.3 + 3.4)
- `requests`, parsing JSON, timeouts and errors, showing API data in a template, notification example.
- AI check: AI reviews relationships and edge cases and suggests tests. We keep what runs and passes, and show one suggestion we reject and why.
- CO3 recap card.
- Mistake: calling an API with no timeout or error handling.

### CO4: Complete, secure, presented app (3 parts)

**Part 10: Design the Complete Application** (LO 4.1)
- Project planning, modular apps, MVT coordination, how the pieces integrate, notification on booking.
- Mistake: one giant app.

**Part 11: Authentication, Permissions, and Security** (LO 4.2)
- Django auth, user roles, permissions, CSRF, password hashing, secure storage of secrets, `check --deploy`.
- Mistake: leaving `DEBUG=True` and a committed `SECRET_KEY`.

**Part 12: AI-Assisted Debugging, Optimization, and Final Presentation** (LO 4.3 + CO4)
- AI-assisted debugging on a planted bug, error analysis, refactor, a performance fix with measured results, justifying design/security/performance decisions, how to present the project.
- CO4 recap and a full course recap of CO1 to CO4.
- Mistake: accepting AI-generated code without reading it.
- As built: a "Find a room" page with one `Exists()` query; a bug report (multi-valued `exclude()`) reproduced, fixed and locked with tests; a measurement on 100,000 bookings (N+1, one query, one query with a composite index); `seed_demo`; `docs/DECISIONS.md` and `docs/PRESENTATION.md`. LO 4.3 in the syllabus reads "Debug and refine code using AI-assisted suggestions and code reviews".

## Scope boundaries

**In scope:** Python scripting, HTTP basics, REST vs SOAP, Django project/app/URL/view/template/model/form, ORM and CRUD, consuming a REST API, built-in auth, CSRF and password hashing, AI-assisted review and debugging, project presentation.

**Out of scope (said on screen):** Django REST Framework (mentioned as a next step), cloud deployment, Docker, JavaScript front-end frameworks, Celery and real email servers, PostgreSQL in practice.

## Deliverables per part

- MP4 (5 to 6 min) with burned-in captions and an SRT
- Thumbnail with a PART N OF 12 badge
- YouTube kit: title, description, tags, chapters, pinned comment, setup sheet
- Code folder `01-...` to `12-...` with tests and README (Parts 1 to 3 are scripts; 4 to 12 are the growing Django project)
- 1 to 2 Shorts per part
- **Quiz:** 4 or 5 multiple-choice questions per part (`quiz.md` in each kit). From Part 5 on, the video ends with a "Check yourself" slide with 3 of them. The course ends with a final quiz covering CO1 to CO4 (`kits\final-course-quiz.md`, extended as each part is built)

Plus series playlist, GitHub README, upload checklist, and schedule.

## Suggested schedule (Thursdays, after EF Core Part 10)

| Part | Date | Part | Date |
|---|---|---|---|
| 1 | 18 Mar 2027 | 7 | 29 Apr |
| 2 | 25 Mar | 8 | 6 May |
| 3 | 1 Apr | 9 | 13 May |
| 4 | 8 Apr | 10 | 20 May |
| 5 | 15 Apr | 11 | 27 May |
| 6 | 22 Apr | 12 | 3 Jun |

## Build order and quality checks

1. For each part: write the code, run it and the tests, and only then write the narration from the working code.
2. Slides use real terminal output. Disclose the synthetic voice and cartoon presenter in YouTube settings and in each description.
3. Render to a temp file, verify with ffmpeg decode, then replace the final file (same rule as EF Core).
4. Pin Django and Python versions in `requirements.txt` so the code still runs when versions move.
5. Reuse `D:\MIT\series-tools\efcore\` scripts (`build_partN`, `assets_partN`, `presenter.py`) as the base for a new `D:\MIT\series-tools\django\` folder.

## Syllabus notes worth your attention

- Your syllabus references Django docs 5.1 and 6.0; I propose 6.1 because it is the newest release, but Django **5.2 is the long-term-support release** if you want the longest-lived code. Tell me which.
- The learning plan lists the course description as "Integrative Programming Technologies 1" but the program as "BSIT - Mobile and Application Development" while the page header also shows an Entertainment and Multimedia (EMC) program objectives table. I did not use that table. You may want to correct it in the syllabus.
- Hours in the plan (13 + 2 per CO, 2 + 13 for CO4) differ in sync/async mix for CO4; the videos support the async hours.
