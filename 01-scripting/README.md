# Part 1: Scripting Languages for Integration (LO 1.1)

The same small integration job, written in Python and in JavaScript: fetch the public holidays of the Philippines for a year from the free [Nager.Date](https://date.nager.at) API, and count how many fall on a school day (Monday to Friday).

## Course outcome

- **CO1:** Explain and analyze scripting concepts and client-server architecture used in application and systems integration.
- **LO 1.1:** Explain the fundamentals of scripting languages (Python, JavaScript, etc.) and their role in system integration.

## Run it

You need Python 3.12+ and Node.js 18+. There is nothing to install.

```bash
python holidays.py          # defaults to 2027
python holidays.py 2028
node holidays.js
node holidays.js 2028
```

The scripts need an internet connection. The output is the same in both languages:

```
2027-01-01  New Year's Day
2027-03-25  Maundy Thursday
...
11 of 18 holidays fall on a school day.
```

## Test it

The tests use a fake response, so they run offline.

```bash
python -m unittest -v       # 5 tests
node --test                 # 3 tests
```

## Files

| File | What it shows |
|---|---|
| `holidays.py` | `urlopen` with a timeout, `json.load`, a list comprehension |
| `holidays.js` | `fetch` with `async`/`await`, `response.json()`, `filter` |
| `test_holidays.py` | weekday logic, formatting, parsing JSON, the timeout |
| `holidays.test.js` | weekday logic and formatting |

## Practice

1. Change the country code from `PH` to another country.
2. Print the number of holidays in each month.
3. Write the same filter in a third language you know.
