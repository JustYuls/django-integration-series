from django.core.management.base import BaseCommand, CommandError

from holiday_api.client import HolidayServiceError, fetch_holidays


class Command(BaseCommand):
    help = "Call the public holidays API and print the holidays that fall on a weekday."

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)
        parser.add_argument("--country", default="PH")

    def handle(self, *args, **options):
        try:
            holidays = fetch_holidays(options["year"], options["country"])
        except HolidayServiceError as error:
            raise CommandError(f"The holidays service is not available: {error}") from error
        weekdays = [h for h in holidays if h["date"].weekday() < 5]
        for holiday in weekdays:
            self.stdout.write(f"{holiday['date']}  {holiday['name']}")
        self.stdout.write(f"{len(weekdays)} of {len(holidays)} holidays fall on a weekday.")
