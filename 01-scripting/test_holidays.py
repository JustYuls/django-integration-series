import io
import json
import unittest
from unittest.mock import patch

import holidays

SAMPLE = [
    {"date": "2027-01-01", "name": "New Year's Day"},   # Friday
    {"date": "2027-02-06", "name": "Chinese New Year"},  # Saturday
    {"date": "2027-03-25", "name": "Maundy Thursday"},   # Thursday
]


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class HolidayTests(unittest.TestCase):
    def test_weekday_is_detected(self):
        self.assertTrue(holidays.is_weekday(SAMPLE[0]))

    def test_weekend_is_detected(self):
        self.assertFalse(holidays.is_weekday(SAMPLE[1]))

    def test_holiday_is_formatted_for_printing(self):
        self.assertEqual(holidays.format_holiday(SAMPLE[0]), "2027-01-01  New Year's Day")

    def test_fetch_turns_json_into_python_objects(self):
        body = FakeResponse(json.dumps(SAMPLE).encode())
        with patch("holidays.urlopen", return_value=body) as fake:
            result = holidays.fetch_holidays(2027)
        self.assertEqual(result, SAMPLE)
        self.assertIn("/2027/PH", fake.call_args.args[0])

    def test_a_timeout_is_always_passed_to_the_request(self):
        body = FakeResponse(b"[]")
        with patch("holidays.urlopen", return_value=body) as fake:
            holidays.fetch_holidays(2027)
        self.assertEqual(fake.call_args.kwargs["timeout"], 10)


if __name__ == "__main__":
    unittest.main()
