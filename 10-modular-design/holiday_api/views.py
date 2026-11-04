from django.shortcuts import render
from django.views.decorators.http import require_GET

from .client import HolidayServiceError, fetch_holidays


@require_GET
def holiday_list(request, year):
    try:
        context = {"year": year, "holidays": fetch_holidays(year), "error": False}
    except HolidayServiceError:
        context = {"year": year, "holidays": [], "error": True}  # degrade gracefully, never crash
    return render(request, "holiday_api/holidays.html", context)
