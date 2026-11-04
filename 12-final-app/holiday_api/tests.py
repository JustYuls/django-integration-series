from datetime import date
from io import StringIO
from unittest import mock

import requests
from django.core.cache import cache
from django.core.management import CommandError, call_command
from django.test import TestCase
from django.urls import reverse

from holiday_api import client
from holiday_api.client import HolidayServiceError, fetch_holidays, holiday_on

GOOD = [{"date": "2027-01-01", "name": "New Year's Day"}, {"date": "2027-12-30", "name": "Rizal Day"}]
HOLIDAYS = [{"date": date(2027, 1, 1), "name": "New Year's Day"}, {"date": date(2027, 12, 30), "name": "Rizal Day"}]


class FakeResponse:
    def __init__(self, status=200, payload=None, bad_json=False):
        self.status_code, self.payload, self.bad_json = status, payload, bad_json

    def json(self):
        if self.bad_json:
            raise ValueError("not json")
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))


class ClientTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_returns_dates_and_names(self):
        with mock.patch("requests.get", return_value=FakeResponse(payload=GOOD)):
            self.assertEqual(fetch_holidays(2027), HOLIDAYS)

    def test_a_timeout_is_always_passed(self):
        with mock.patch("requests.get", return_value=FakeResponse(payload=GOOD)) as get:
            fetch_holidays(2027)
        self.assertEqual(get.call_args.kwargs["timeout"], client.TIMEOUT)

    def test_every_failure_becomes_one_error(self):
        failures = [
            mock.patch("requests.get", return_value=FakeResponse(status=500, payload={})),
            mock.patch("requests.get", return_value=FakeResponse(bad_json=True)),
            mock.patch("requests.get", side_effect=requests.ConnectionError("down")),
            mock.patch("requests.get", side_effect=requests.Timeout("slow")),
            mock.patch("requests.get", return_value=FakeResponse(payload=[{"name": "no date"}])),
        ]
        for failure in failures:
            cache.clear()
            with failure, self.assertLogs("holiday_api.client", level="WARNING"):
                with self.assertRaises(HolidayServiceError):
                    fetch_holidays(2027)

    def test_no_content_gives_an_empty_list(self):
        with mock.patch("requests.get", return_value=FakeResponse(status=204, bad_json=True)):
            self.assertEqual(fetch_holidays(2027), [])

    def test_the_second_call_uses_the_cache(self):
        with mock.patch("requests.get", return_value=FakeResponse(payload=GOOD)) as get:
            fetch_holidays(2027)
            fetch_holidays(2027)
        self.assertEqual(get.call_count, 1)

    def test_a_failure_is_not_cached(self):
        with mock.patch("requests.get", side_effect=requests.ConnectionError("down")), self.assertLogs("holiday_api.client", level="WARNING"):
            with self.assertRaises(HolidayServiceError):
                fetch_holidays(2027)
        with mock.patch("requests.get", return_value=FakeResponse(payload=GOOD)):
            self.assertEqual(len(fetch_holidays(2027)), 2)

    def test_holiday_on(self):
        with mock.patch("holiday_api.client.fetch_holidays", return_value=HOLIDAYS):
            self.assertEqual(holiday_on(date(2027, 1, 1)), "New Year's Day")
            self.assertIsNone(holiday_on(date(2027, 1, 4)))
        with mock.patch("holiday_api.client.fetch_holidays", side_effect=HolidayServiceError("down")):
            self.assertIsNone(holiday_on(date(2027, 1, 1)))


class PageAndCommandTests(TestCase):
    def test_the_page_lists_holidays(self):
        with mock.patch("holiday_api.views.fetch_holidays", return_value=HOLIDAYS):
            response = self.client.get(reverse("holiday_api:holiday_list", args=[2027]))
        self.assertContains(response, "Rizal Day")

    def test_the_page_survives_a_service_failure(self):
        with mock.patch("holiday_api.views.fetch_holidays", side_effect=HolidayServiceError("down")):
            response = self.client.get(reverse("holiday_api:holiday_list", args=[2027]))
        self.assertContains(response, "not available right now")

    def test_the_command(self):
        out = StringIO()
        with mock.patch("holiday_api.management.commands.check_holidays.fetch_holidays", return_value=HOLIDAYS):
            call_command("check_holidays", 2027, stdout=out)
        self.assertIn("2 of 2 holidays fall on a weekday.", out.getvalue())
        with mock.patch("holiday_api.management.commands.check_holidays.fetch_holidays", side_effect=HolidayServiceError("down")):
            with self.assertRaises(CommandError):
                call_command("check_holidays", 2027)
