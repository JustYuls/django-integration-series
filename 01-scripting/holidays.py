"""Part 1: a Python script that fetches public holidays and reports the school days they cost."""
import json
import sys
from datetime import date
from urllib.request import urlopen

URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/{country}"


def fetch_holidays(year, country="PH"):
    # Ask the server for JSON and turn it into Python lists and dictionaries.
    with urlopen(URL.format(year=year, country=country), timeout=10) as response:
        return json.load(response)


def is_weekday(holiday):
    return date.fromisoformat(holiday["date"]).weekday() < 5


def format_holiday(holiday):
    return f"{holiday['date']}  {holiday['name']}"


def main():
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2027
    holidays = fetch_holidays(year)
    weekday_holidays = [h for h in holidays if is_weekday(h)]
    for holiday in weekday_holidays:
        print(format_holiday(holiday))
    print(f"{len(weekday_holidays)} of {len(holidays)} holidays fall on a school day.")


if __name__ == "__main__":
    main()
