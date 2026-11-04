from datetime import timedelta
from unittest import mock

from django.core import mail
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from bookings import services
from bookings.forms import LOCAL_FORMAT, BookingForm
from bookings.models import Booking
from rooms.models import Room


def local(dt):
    return timezone.localtime(dt).strftime(LOCAL_FORMAT)


class DataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(name="Room 101", capacity=40)
        cls.lab = Room.objects.create(name="Lab A", capacity=30)
        cls.start = timezone.now() + timedelta(days=2)
        cls.end = cls.start + timedelta(hours=2)

    def make_booking(self, room=None, by="Ana", purpose="Review", days=2, hours=2, email=""):
        start = timezone.now() + timedelta(days=days)
        return Booking.objects.create(room=room or self.room, booked_by=by, purpose=purpose, booker_email=email, start=start, end=start + timedelta(hours=hours))

    def form_data(self, **changes):
        data = {"room": self.room.pk, "booked_by": "Ana", "booker_email": "ana@example.com", "purpose": "Review", "attendees": 10,
                "start": local(self.start), "end": local(self.end)}
        data.update(changes)
        return data


class ModelTests(DataMixin, TestCase):
    def test_a_booking_must_end_after_it_starts(self):
        with self.assertRaises(ValidationError):
            Booking(room=self.room, booked_by="Ana", start=self.end, end=self.start).full_clean()

    def test_upcoming_and_matching(self):
        self.make_booking(by="Ana", purpose="Exam review")
        past = timezone.now() - timedelta(days=3)
        Booking.objects.create(room=self.room, booked_by="Old", start=past, end=past + timedelta(hours=1))
        self.assertEqual(Booking.objects.upcoming().count(), 1)
        self.assertEqual(Booking.objects.matching("REVIEW").count(), 1)

    def test_a_room_with_bookings_cannot_be_deleted_at_the_database_level(self):
        self.make_booking()
        with self.assertRaises(ProtectedError):
            self.room.delete()


class FormTests(DataMixin, TestCase):
    def test_a_valid_form(self):
        self.assertTrue(BookingForm(self.form_data()).is_valid())

    def test_over_capacity_and_double_booking_are_rejected(self):
        self.assertIn("attendees", BookingForm(self.form_data(attendees=99)).errors)
        Booking.objects.create(room=self.room, booked_by="Ben", start=self.start, end=self.end)
        self.assertFalse(BookingForm(self.form_data()).is_valid())

    def test_editing_does_not_clash_with_itself(self):
        booking = Booking.objects.create(room=self.room, booked_by="Ana", start=self.start, end=self.end)
        self.assertTrue(BookingForm(self.form_data(booked_by="Ana B."), instance=booking).is_valid())

    @override_settings(HOLIDAYS_ENABLED=True)
    def test_a_holiday_is_rejected_through_the_holiday_app(self):
        with mock.patch("bookings.forms.holiday_on", return_value="Rizal Day"):
            form = BookingForm(self.form_data())
            errors = form.errors
        self.assertIn("public holiday: Rizal Day", errors["start"][0])


class ServiceTests(DataMixin, TestCase):
    def test_book_room_saves_and_sends_the_email(self):
        form = BookingForm(self.form_data())
        self.assertTrue(form.is_valid())
        booking = services.book_room(form)
        self.assertEqual(Booking.objects.get(), booking)
        self.assertEqual(len(mail.outbox), 1)

    def test_a_mail_failure_never_undoes_or_hides_a_saved_booking(self):
        form = BookingForm(self.form_data())
        form.is_valid()
        with mock.patch("bookings.services.send_booking_confirmation", side_effect=RuntimeError("smtp down")):
            with self.assertLogs("bookings.services", level="ERROR"):
                services.book_room(form)
        self.assertEqual(Booking.objects.count(), 1)

    def test_cancel_booking_deletes_it(self):
        booking = self.make_booking()
        services.cancel_booking(booking)
        self.assertEqual(Booking.objects.count(), 0)


class ViewTests(DataMixin, TestCase):
    def test_create_saves_redirects_and_emails(self):
        response = self.client.post(reverse("bookings:booking_create"), self.form_data(), follow=True)
        self.assertContains(response, "Booking saved.")
        self.assertEqual(len(mail.outbox), 1)

    def test_an_invalid_post_shows_errors_and_saves_nothing(self):
        response = self.client.post(reverse("bookings:booking_create"), self.form_data(attendees=500))
        self.assertContains(response, "seats only 40")
        self.assertEqual(Booking.objects.count(), 0)

    def test_update_and_delete_flow(self):
        booking = self.make_booking()
        data = self.form_data(booked_by="Changed", start=local(booking.start), end=local(booking.end))
        self.client.post(reverse("bookings:booking_update", args=[booking.pk]), data)
        booking.refresh_from_db()
        self.assertEqual(booking.booked_by, "Changed")
        self.assertContains(self.client.get(reverse("bookings:booking_delete", args=[booking.pk])), "Delete this booking?")
        self.assertEqual(Booking.objects.count(), 1)
        self.client.post(reverse("bookings:booking_delete", args=[booking.pk]))
        self.assertEqual(Booking.objects.count(), 0)

    def test_a_post_without_a_csrf_token_is_403(self):
        booking = self.make_booking()
        self.assertEqual(Client(enforce_csrf_checks=True).post(reverse("bookings:booking_delete", args=[booking.pk])).status_code, 403)

    def test_the_list_filters_searches_and_paginates(self):
        for d in range(2, 9):
            self.make_booking(days=d, by=f"P{d}", purpose="Review" if d % 2 else "Workshop")
        self.make_booking(room=self.lab, days=12, by="Lab user")
        url = reverse("bookings:booking_list")
        self.assertEqual(self.client.get(url).context["page"].paginator.num_pages, 2)
        self.assertEqual([b.booked_by for b in self.client.get(url, {"room": self.lab.pk}).context["page"]], ["Lab user"])
        self.assertEqual(self.client.get(url, {"q": "workshop"}).context["page"].paginator.count, 4)
        self.assertEqual(self.client.get(url, {"room": "x'; DROP"}).status_code, 200)

    def test_the_list_page_uses_three_queries_however_many_rows(self):
        for d in range(2, 6):
            self.make_booking(days=d)
        with self.assertNumQueries(3):
            self.client.get(reverse("bookings:booking_list"))

    def test_the_room_schedule_page(self):
        self.make_booking(by="Scheduled")
        response = self.client.get(reverse("bookings:room_schedule", args=[self.room.pk]))
        self.assertContains(response, "Scheduled")
        self.assertEqual(self.client.get(reverse("bookings:room_schedule", args=[999])).status_code, 404)
