"""A small client for the public Nager.Date holidays API. This app has no models and imports no other app."""
import logging
from datetime import date

import requests
from django.core.cache import cache

API_URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/{country}"
TIMEOUT = 5  # seconds: never call another system without a timeout
CACHE_SECONDS = 24 * 60 * 60

log = logging.getLogger(__name__)


class HolidayServiceError(Exception):
    """The holidays service is down, slow, or answered with something we cannot use."""


def fetch_holidays(year, country="PH"):
    """Return the holidays of a year as [{"date": date, "name": str}, ...]."""
    key = f"holidays:{country}:{year}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    try:
        response = requests.get(API_URL.format(year=year, country=country), timeout=TIMEOUT)
        response.raise_for_status()
        if response.status_code == 204:
            return []
        holidays = [{"date": date.fromisoformat(item["date"]), "name": item["name"]} for item in response.json()]
    except (requests.RequestException, ValueError, KeyError, TypeError) as error:
        log.warning("Holidays API failed: %s", error)
        raise HolidayServiceError(str(error)) from error
    cache.set(key, holidays, CACHE_SECONDS)
    return holidays


def holiday_on(day, country="PH"):
    """The name of the holiday on a date, or None. If the service fails, bookings still work."""
    try:
        for holiday in fetch_holidays(day.year, country):
            if holiday["date"] == day:
                return holiday["name"]
    except HolidayServiceError:
        return None
    return None
