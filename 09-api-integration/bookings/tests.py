from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from bookings.forms import LOCAL_FORMAT, BookingForm
from bookings.models import Booking, Room


def local(dt):
    return timezone.localtime(dt).strftime(LOCAL_FORMAT)


class DataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(name="Room 101", capacity=40, has_projector=True)
        cls.lab = Room.objects.create(name="Lab A", capacity=30)
        cls.start = timezone.now() + timedelta(days=1)
        cls.end = cls.start + timedelta(hours=2)

    def make_booking(self, room=None, by="Ana", purpose="Review", days=1, hours=2):
        start = timezone.now() + timedelta(days=days)
        return Booking.objects.create(room=room or self.room, booked_by=by, purpose=purpose, start=start, end=start + timedelta(hours=hours))

    def form_data(self, **changes):
        data = {"room": self.room.pk, "booked_by": "Ana", "purpose": "Review", "attendees": 10, "start": local(self.start), "end": local(self.end)}
        data.update(changes)
        return data


class ModelAndQuerySetTests(DataMixin, TestCase):
    def test_rooms_are_ordered_by_name(self):
        self.assertEqual([r.name for r in Room.objects.all()], ["Lab A", "Room 101"])

    def test_a_booking_must_end_after_it_starts(self):
        with self.assertRaises(ValidationError):
            Booking(room=self.room, booked_by="Ana", start=self.end, end=self.start).full_clean()

    def test_deleting_a_room_deletes_its_bookings(self):
        self.make_booking()
        self.room.delete()
        self.assertEqual(Booking.objects.count(), 0)

    def test_with_booking_counts_annotates_each_room(self):
        self.make_booking()
        self.make_booking(days=3)
        counts = {r.name: r.booking_count for r in Room.objects.with_booking_counts()}
        self.assertEqual(counts, {"Lab A": 0, "Room 101": 2})

    def test_upcoming_hides_bookings_that_already_ended(self):
        self.make_booking(days=1)
        past = timezone.now() - timedelta(days=2)
        Booking.objects.create(room=self.room, booked_by="Old", start=past, end=past + timedelta(hours=1))
        self.assertEqual([b.booked_by for b in Booking.objects.upcoming()], ["Ana"])

    def test_matching_searches_purpose_and_name_case_insensitively(self):
        self.make_booking(by="Ana", purpose="Exam review")
        self.make_booking(by="Ben", purpose="Workshop", days=3)
        self.assertEqual(Booking.objects.matching("REVIEW").count(), 1)
        self.assertEqual(Booking.objects.matching("ben").count(), 1)

    def test_for_room_filters_by_room(self):
        self.make_booking()
        self.make_booking(room=self.lab, days=3)
        self.assertEqual(Booking.objects.for_room(self.lab).count(), 1)


class LazinessAndQueryCountTests(DataMixin, TestCase):
    def test_building_a_queryset_runs_no_query(self):
        with self.assertNumQueries(0):
            Booking.objects.filter(attendees__gte=1).order_by("-start")

    def test_evaluating_a_queryset_runs_one_query(self):
        self.make_booking()
        qs = Booking.objects.filter(attendees__gte=1)
        with self.assertNumQueries(1):
            list(qs)

    def test_a_queryset_is_cached_after_the_first_evaluation(self):
        self.make_booking()
        qs = Booking.objects.all()
        list(qs)
        with self.assertNumQueries(0):
            list(qs)

    def test_touching_room_for_every_booking_costs_one_query_per_row(self):
        for d in range(1, 5):
            self.make_booking(days=d)
        with self.assertNumQueries(1 + 4):  # the N+1 problem
            [b.room.name for b in Booking.objects.all()]

    def test_select_related_makes_it_a_single_query(self):
        for d in range(1, 5):
            self.make_booking(days=d)
        with self.assertNumQueries(1):
            [b.room.name for b in Booking.objects.select_related("room")]

    def test_the_booking_list_page_uses_three_queries_however_many_rows(self):
        for d in range(1, 5):
            self.make_booking(days=d)
        with self.assertNumQueries(3):  # rooms for the filter, the paginator count, the page
            self.client.get(reverse("bookings:booking_list"))


class FormTests(DataMixin, TestCase):
    def test_a_valid_form_saves(self):
        form = BookingForm(self.form_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_a_double_booking_is_rejected(self):
        Booking.objects.create(room=self.room, booked_by="Ben", start=self.start, end=self.end)
        self.assertFalse(BookingForm(self.form_data()).is_valid())

    def test_editing_a_booking_does_not_clash_with_itself(self):
        booking = Booking.objects.create(room=self.room, booked_by="Ana", start=self.start, end=self.end)
        form = BookingForm(self.form_data(booked_by="Ana B."), instance=booking)
        self.assertTrue(form.is_valid(), form.errors)

    def test_over_capacity_is_rejected(self):
        self.assertIn("attendees", BookingForm(self.form_data(attendees=99)).errors)


class BookingCrudViewTests(DataMixin, TestCase):
    def test_create_saves_redirects_and_shows_a_message(self):
        response = self.client.post(reverse("bookings:booking_create"), self.form_data(), follow=True)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertContains(response, "Booking saved.")

    def test_read_the_list_shows_every_booking(self):
        self.make_booking()
        self.assertContains(self.client.get(reverse("bookings:booking_list")), "Ana")

    def test_update_form_is_prefilled(self):
        booking = self.make_booking(by="Prefilled")
        self.assertContains(self.client.get(reverse("bookings:booking_update", args=[booking.pk])), "Prefilled")

    def test_update_changes_the_row(self):
        booking = self.make_booking()
        data = self.form_data(booked_by="Changed", start=local(booking.start), end=local(booking.end))
        response = self.client.post(reverse("bookings:booking_update", args=[booking.pk]), data, follow=True)
        booking.refresh_from_db()
        self.assertEqual(booking.booked_by, "Changed")
        self.assertContains(response, "Booking updated.")

    def test_update_of_a_missing_booking_is_404(self):
        self.assertEqual(self.client.get(reverse("bookings:booking_update", args=[999])).status_code, 404)

    def test_delete_get_only_asks_for_confirmation(self):
        booking = self.make_booking()
        response = self.client.get(reverse("bookings:booking_delete", args=[booking.pk]))
        self.assertContains(response, "Delete this booking?")
        self.assertEqual(Booking.objects.count(), 1)

    def test_delete_post_removes_the_row(self):
        booking = self.make_booking()
        response = self.client.post(reverse("bookings:booking_delete", args=[booking.pk]), follow=True)
        self.assertEqual(Booking.objects.count(), 0)
        self.assertContains(response, "Booking deleted.")

    def test_a_post_without_a_csrf_token_is_403(self):
        booking = self.make_booking()
        strict = Client(enforce_csrf_checks=True)
        self.assertEqual(strict.post(reverse("bookings:booking_delete", args=[booking.pk])).status_code, 403)
        self.assertEqual(Booking.objects.count(), 1)


class FilteringAndPaginationTests(DataMixin, TestCase):
    def setUp(self):
        for d in range(1, 8):
            self.make_booking(days=d, by=f"Person {d}", purpose="Review" if d % 2 else "Workshop")
        self.make_booking(room=self.lab, days=10, by="Lab user")

    def test_the_list_is_paginated_five_per_page(self):
        response = self.client.get(reverse("bookings:booking_list"))
        self.assertEqual(len(response.context["page"]), 5)
        self.assertEqual(response.context["page"].paginator.num_pages, 2)

    def test_page_two_has_the_rest(self):
        self.assertEqual(len(self.client.get(reverse("bookings:booking_list"), {"page": 2}).context["page"]), 3)

    def test_a_bad_page_number_falls_back_to_a_real_page(self):
        self.assertEqual(self.client.get(reverse("bookings:booking_list"), {"page": "abc"}).status_code, 200)

    def test_filter_by_room(self):
        response = self.client.get(reverse("bookings:booking_list"), {"room": self.lab.pk})
        self.assertEqual([b.booked_by for b in response.context["page"]], ["Lab user"])

    def test_a_non_numeric_room_filter_is_ignored(self):
        self.assertEqual(self.client.get(reverse("bookings:booking_list"), {"room": "x'; DROP"}).status_code, 200)

    def test_search_text_filters_rows(self):
        response = self.client.get(reverse("bookings:booking_list"), {"q": "workshop"})
        self.assertEqual(response.context["page"].paginator.count, 3)

    def test_a_hostile_search_string_is_only_text(self):
        response = self.client.get(reverse("bookings:booking_list"), {"q": "x'; DROP TABLE bookings_booking; --"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"].paginator.count, 0)
        self.assertEqual(Booking.objects.count(), 8)  # the table and its rows are untouched

    def test_the_filter_and_search_combine(self):
        response = self.client.get(reverse("bookings:booking_list"), {"room": self.room.pk, "q": "Review"})
        self.assertEqual(response.context["page"].paginator.count, 4)


class RoomCrudViewTests(DataMixin, TestCase):
    def test_room_list_shows_booking_counts(self):
        self.make_booking()
        page = self.client.get(reverse("bookings:room_list")).content.decode()
        self.assertIn("1 booking", page)
        self.assertIn("0 bookings", page)

    def test_create_a_room(self):
        response = self.client.post(reverse("bookings:room_create"), {"name": "Gym", "capacity": 80}, follow=True)
        self.assertTrue(Room.objects.filter(name="Gym").exists())
        self.assertContains(response, "Room created.")

    def test_create_rejects_a_duplicate_name(self):
        response = self.client.post(reverse("bookings:room_create"), {"name": "Lab A", "capacity": 5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Room.objects.filter(name="Lab A").count(), 1)

    def test_update_a_room(self):
        self.client.post(reverse("bookings:room_update", args=[self.lab.pk]), {"name": "Lab B", "capacity": 35})
        self.lab.refresh_from_db()
        self.assertEqual((self.lab.name, self.lab.capacity), ("Lab B", 35))

    def test_delete_confirmation_warns_about_bookings(self):
        self.make_booking()
        self.assertContains(self.client.get(reverse("bookings:room_delete", args=[self.room.pk])), "also deletes its 1 booking")

    def test_delete_a_room_cascades_to_its_bookings(self):
        self.make_booking()
        self.client.post(reverse("bookings:room_delete", args=[self.room.pk]))
        self.assertFalse(Room.objects.filter(pk=self.room.pk).exists())
        self.assertEqual(Booking.objects.count(), 0)
