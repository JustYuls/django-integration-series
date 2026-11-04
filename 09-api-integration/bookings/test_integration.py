"""Part 9 tests: the holidays API, the form, the page, e-mail, and the command. No test calls the real network."""
from datetime import date, timedelta
from io import StringIO
from unittest import mock

from django.core import mail
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from bookings.forms import LOCAL_FORMAT, BookingForm
from bookings.holidays import HolidayServiceError, holiday_on
from bookings.models import Booking, Room
from bookings.notifications import send_booking_confirmation

HOLIDAYS = [{"date": date(2027, 1, 1), "name": "New Year's Day"}, {"date": date(2027, 12, 30), "name": "Rizal Day"}]


def local(dt):
    return timezone.localtime(dt).strftime(LOCAL_FORMAT)


class Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(name="Room 101", capacity=40)
        cls.start = timezone.now() + timedelta(days=2)
        cls.end = cls.start + timedelta(hours=2)

    def data(self, **changes):
        data = {"room": self.room.pk, "booked_by": "Ana", "booker_email": "ana@example.com", "purpose": "", "attendees": 5,
                "start": local(self.start), "end": local(self.end)}
        data.update(changes)
        return data


class HolidayLookupTests(TestCase):
    def test_holiday_on_returns_the_name_on_a_holiday(self):
        with mock.patch("bookings.holidays.fetch_holidays", return_value=HOLIDAYS):
            self.assertEqual(holiday_on(date(2027, 1, 1)), "New Year's Day")

    def test_holiday_on_returns_none_on_a_normal_day(self):
        with mock.patch("bookings.holidays.fetch_holidays", return_value=HOLIDAYS):
            self.assertIsNone(holiday_on(date(2027, 1, 4)))

    def test_holiday_on_returns_none_when_the_service_fails(self):
        with mock.patch("bookings.holidays.fetch_holidays", side_effect=HolidayServiceError("down")):
            self.assertIsNone(holiday_on(date(2027, 1, 1)))


@override_settings(HOLIDAYS_ENABLED=True)
class FormHolidayTests(Base):
    def test_a_booking_on_a_holiday_is_rejected(self):
        with mock.patch("bookings.forms.holiday_on", return_value="Rizal Day"):
            form = BookingForm(self.data())
            errors = form.errors  # a form validates lazily, so read the errors inside the patch
        self.assertIn("public holiday: Rizal Day", errors["start"][0])

    def test_a_normal_day_is_accepted(self):
        with mock.patch("bookings.forms.holiday_on", return_value=None):
            self.assertTrue(BookingForm(self.data()).is_valid())

    @override_settings(HOLIDAYS_ENABLED=False)
    def test_the_check_can_be_switched_off(self):
        with mock.patch("bookings.forms.holiday_on") as lookup:
            self.assertTrue(BookingForm(self.data()).is_valid())
        lookup.assert_not_called()

    def test_tests_do_not_hit_the_network_by_default(self):
        # settings.HOLIDAYS_ENABLED is False while running "manage.py test"
        with override_settings(HOLIDAYS_ENABLED=False):
            self.assertTrue(BookingForm(self.data()).is_valid())


class HolidayPageTests(TestCase):
    def test_the_page_lists_the_holidays_from_the_api(self):
        with mock.patch("bookings.views.fetch_holidays", return_value=HOLIDAYS):
            response = self.client.get(reverse("bookings:holiday_list", args=[2027]))
        self.assertContains(response, "Rizal Day")
        self.assertContains(response, "Fri, Jan 1")

    def test_when_the_service_is_down_the_page_still_loads_with_a_message(self):
        with mock.patch("bookings.views.fetch_holidays", side_effect=HolidayServiceError("down")):
            response = self.client.get(reverse("bookings:holiday_list", args=[2027]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not available right now")


class NotificationTests(Base):
    def test_a_confirmation_email_is_sent(self):
        booking = Booking.objects.create(room=self.room, booked_by="Ana", booker_email="ana@example.com", start=self.start, end=self.end)
        self.assertEqual(send_booking_confirmation(booking), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ana@example.com"])
        self.assertIn("Room 101", mail.outbox[0].subject)

    def test_no_email_without_an_address(self):
        booking = Booking.objects.create(room=self.room, booked_by="Ana", start=self.start, end=self.end)
        self.assertEqual(send_booking_confirmation(booking), 0)
        self.assertEqual(mail.outbox, [])

    def test_creating_a_booking_through_the_view_sends_the_email(self):
        self.client.post(reverse("bookings:booking_create"), self.data())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Hi Ana", mail.outbox[0].body)

    def test_an_invalid_booking_sends_nothing(self):
        self.client.post(reverse("bookings:booking_create"), self.data(attendees=999))
        self.assertEqual(mail.outbox, [])


class CommandTests(TestCase):
    def test_the_command_prints_weekday_holidays(self):
        out = StringIO()
        with mock.patch("bookings.management.commands.check_holidays.fetch_holidays", return_value=HOLIDAYS):
            call_command("check_holidays", 2027, stdout=out)
        self.assertIn("2027-01-01  New Year's Day", out.getvalue())
        self.assertIn("2 of 2 holidays fall on a weekday.", out.getvalue())

    def test_the_command_reports_a_clear_error_when_the_service_is_down(self):
        with mock.patch("bookings.management.commands.check_holidays.fetch_holidays", side_effect=HolidayServiceError("down")):
            with self.assertRaises(CommandError):
                call_command("check_holidays", 2027)
