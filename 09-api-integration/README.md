# Part 9: Consuming an External API, Validated with AI-Assisted Tests (LO 3.3 and 3.4)

The Campus Booking Hub calls a free public API (Nager.Date) to learn about public holidays. The client uses `requests` with a timeout, turns every failure into one clear error, and caches answers. Bookings send a notification, and a management command checks holidays. A `holiday_review` package runs the test scenarios an AI assistant suggested against a naive client and the fixed one.

## Course outcome

- **CO3:** Develop dynamic, data-driven Django applications by implementing templates, models, database integration, CRUD operations, and API consumption, while using Generative AI to validate logic, improve data handling, and enhance integration workflows.
- **LO 3.3:** Consume external APIs and integrate their data into Django apps.
- **LO 3.4:** Validate application logic, data flows, and model relationships using AI-assisted testing or code review.

## Set it up

Use the virtual environment from Part 4, then:

```bash
cd 09-api-integration
pip install -r requirements.txt     # adds requests
python manage.py migrate
python manage.py runserver
```

Open `/holidays/2027/` to see the holiday page. The network is used only when you run the server; tests never touch it.

```bash
python manage.py check_holidays 2027     # prints the holidays, or a friendly error
```

## Test it

```bash
python manage.py test           # 67 tests, all offline (the API is mocked)
```

## The AI test review

```bash
python -m holiday_review.review
```

```
SCENARIO (suggested by the AI)                   naive  fixed
returns the holidays on a 200 answer             PASS   PASS
passes a timeout to requests                     FAIL   PASS
HTTP 500 becomes HolidayServiceError             FAIL   PASS
invalid JSON becomes HolidayServiceError         FAIL   PASS
connection error becomes HolidayServiceError     FAIL   PASS
204 No Content gives an empty list               FAIL   PASS
a malformed item becomes HolidayServiceError     FAIL   PASS
the second call uses the cache                   FAIL   PASS
naive: 1 of 8 pass.   fixed: 8 of 8 pass.
```

The AI suggestions used in the video were generated with Claude (Anthropic), shortened, and run as real tests. We keep what passes, and show one suggestion we reject and why.

## What is in the folder

| Path | What it is |
|---|---|
| `bookings/holidays.py` | `fetch_holidays`, `holiday_on`, and `HolidayServiceError` (timeout, status, JSON, shape, cache) |
| `bookings/notifications.py` | booking confirmation e-mail that never breaks the booking |
| `bookings/management/commands/check_holidays.py` | the command-line check |
| `bookings/templates/bookings/holidays.html` | the holiday page, with a friendly message when the service is down |
| `bookings/test_integration.py` | integration tests with mocks |
| `holiday_review/` | the naive client, the scenario runner, and its tests |

## Practice

1. Remove `timeout=` from the client. Which test fails, and why does a missing timeout matter?
2. Make the API return a 500. What does the holiday page show?
3. Write one more scenario for the AI list (for example, a very large answer) and run it against the fixed client.
