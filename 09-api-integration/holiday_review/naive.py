"""The first, naive version of the holidays client: the one an AI draft might give you (Part 9).
It works when everything goes right. The AI-suggested tests show what happens when it does not."""
import requests

from bookings.holidays import API_URL


def naive_fetch_holidays(year, country="PH"):
    response = requests.get(API_URL.format(year=year, country=country))  # no timeout, no status check
    return [{"date": item["date"], "name": item["name"]} for item in response.json()]  # trusts the shape
