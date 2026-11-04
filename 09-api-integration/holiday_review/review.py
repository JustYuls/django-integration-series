"""Part 9: run the edge-case tests an AI suggested against the naive client and the real one.

Run from the project folder:   python -m holiday_review.review
"""
import logging
import os
from unittest import mock

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_hub.settings")
django.setup()

import requests  # noqa: E402
from django.core.cache import cache  # noqa: E402

from bookings.holidays import HolidayServiceError, fetch_holidays  # noqa: E402
from holiday_review.naive import naive_fetch_holidays  # noqa: E402

logging.getLogger("bookings.holidays").setLevel(logging.ERROR)  # the failures are expected here

GOOD = [{"date": "2027-01-01", "name": "New Year's Day"}]


class FakeResponse:
    def __init__(self, status=200, payload=None, bad_json=False):
        self.status_code, self.payload, self.bad_json = status, payload, bad_json

    def json(self):
        if self.bad_json:
            raise ValueError("not json")
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def raises_service_error(call):
    try:
        call()
    except HolidayServiceError:
        return True
    except Exception:  # any other exception means the caller would crash
        return False
    return False


def s_happy(fetch):
    with mock.patch("requests.get", return_value=FakeResponse(payload=GOOD)):
        result = fetch(2027)
    return str(result[0]["date"]) == "2027-01-01" and result[0]["name"] == "New Year's Day"


def s_timeout(fetch):
    with mock.patch("requests.get", return_value=FakeResponse(payload=GOOD)) as get:
        fetch(2027)
    return get.call_args.kwargs.get("timeout", 0) > 0


def s_http_500(fetch):
    with mock.patch("requests.get", return_value=FakeResponse(status=500, payload={"error": "boom"})):
        return raises_service_error(lambda: fetch(2027))


def s_bad_json(fetch):
    with mock.patch("requests.get", return_value=FakeResponse(bad_json=True)):
        return raises_service_error(lambda: fetch(2027))


def s_connection_error(fetch):
    with mock.patch("requests.get", side_effect=requests.ConnectionError("no network")):
        return raises_service_error(lambda: fetch(2027))


def s_no_content(fetch):
    with mock.patch("requests.get", return_value=FakeResponse(status=204, bad_json=True)):
        try:
            return fetch(2027) == []
        except Exception:
            return False


def s_malformed_item(fetch):
    with mock.patch("requests.get", return_value=FakeResponse(payload=[{"name": "no date"}])):
        return raises_service_error(lambda: fetch(2027))


def s_cache(fetch):
    with mock.patch("requests.get", return_value=FakeResponse(payload=GOOD)) as get:
        fetch(2027)
        fetch(2027)
    return get.call_count == 1


SCENARIOS = [
    ("returns the holidays on a 200 answer", s_happy), ("passes a timeout to requests", s_timeout), ("HTTP 500 becomes HolidayServiceError", s_http_500),
    ("invalid JSON becomes HolidayServiceError", s_bad_json), ("connection error becomes HolidayServiceError", s_connection_error),
    ("204 No Content gives an empty list", s_no_content), ("a malformed item becomes HolidayServiceError", s_malformed_item), ("the second call uses the cache", s_cache),
]


def run(fetch):
    results = {}
    for name, scenario in SCENARIOS:
        cache.clear()
        results[name] = scenario(fetch)
    cache.clear()
    return results


def evaluate():
    return {"naive": run(naive_fetch_holidays), "fixed": run(fetch_holidays)}


def main():
    r = evaluate()
    print(f"{'SCENARIO (suggested by the AI)':<48} {'naive':<6} fixed")
    for name, _ in SCENARIOS:
        print(f"{name:<48} {'PASS' if r['naive'][name] else 'FAIL':<6} {'PASS' if r['fixed'][name] else 'FAIL'}")
    print(f"naive: {sum(r['naive'].values())} of {len(SCENARIOS)} pass.   fixed: {sum(r['fixed'].values())} of {len(SCENARIOS)} pass.")


if __name__ == "__main__":
    main()
