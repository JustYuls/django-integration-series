from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.template import Context, Template
from django.test import Client, TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from bookings import views
from bookings.forms import LOCAL_FORMAT, BookingForm
from bookings.models import Booking, Room


def local(dt):
    return timezone.localtime(dt).strftime(LOCAL_FORMAT)  # what a datetime-local input sends


class DataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(name="Room 101", capacity=40, has_projector=True)
        cls.lab = Room.objects.create(name="Lab A", capacity=1)
        cls.start = timezone.now() + timedelta(days=1)
        cls.end = cls.start + timedelta(hours=2)

    def form_data(self, **changes):
        data = {"room": self.room.pk, "booked_by": "Ana", "purpose": "Review", "attendees": 10,
                "start": local(self.start), "end": local(self.end)}
        data.update(changes)
        return data


class ModelTests(DataMixin, TestCase):
    def test_str_shows_the_name(self):
        self.assertEqual(str(self.room), "Room 101")

    def test_rooms_are_ordered_by_name(self):
        self.assertEqual([r.name for r in Room.objects.all()], ["Lab A", "Room 101"])

    def test_a_booking_must_end_after_it_starts(self):
        booking = Booking(room=self.room, booked_by="Ana", start=self.end, end=self.start)
        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_room_names_are_unique(self):
        with self.assertRaises(ValidationError):
            Room(name="Room 101", capacity=5).full_clean()

    def test_deleting_a_room_deletes_its_bookings(self):
        Booking.objects.create(room=self.room, booked_by="Ana", start=self.start, end=self.end)
        self.room.delete()
        self.assertEqual(Booking.objects.count(), 0)


class FormTests(DataMixin, TestCase):
    def test_a_valid_form_saves_a_booking(self):
        form = BookingForm(self.form_data())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().booked_by, "Ana")

    def test_end_before_start_is_rejected(self):
        form = BookingForm(self.form_data(end=local(self.start - timedelta(hours=1))))
        self.assertFalse(form.is_valid())

    def test_a_start_in_the_past_is_rejected(self):
        past = timezone.now() - timedelta(days=1)
        form = BookingForm(self.form_data(start=local(past), end=local(past + timedelta(hours=1))))
        self.assertIn("start", form.errors)

    def test_more_attendees_than_seats_is_rejected(self):
        form = BookingForm(self.form_data(room=self.lab.pk, attendees=5))
        self.assertIn("attendees", form.errors)
        self.assertIn("seats only 1", form.errors["attendees"][0])

    def test_a_double_booking_is_rejected(self):
        Booking.objects.create(room=self.room, booked_by="Ben", start=self.start, end=self.end)
        form = BookingForm(self.form_data())
        self.assertFalse(form.is_valid())
        self.assertIn("already booked", form.non_field_errors()[0])

    def test_the_same_time_in_another_room_is_fine(self):
        Booking.objects.create(room=self.room, booked_by="Ben", start=self.start, end=self.end)
        other = Room.objects.create(name="Gym", capacity=80)
        self.assertTrue(BookingForm(self.form_data(room=other.pk)).is_valid())

    def test_required_fields_are_enforced(self):
        form = BookingForm({})
        for field in ("room", "booked_by", "attendees", "start", "end"):
            self.assertIn(field, form.errors)
        self.assertNotIn("purpose", form.errors)  # blank=True


class ViewTests(DataMixin, TestCase):
    def test_room_list_shows_rooms_from_the_database(self):
        response = self.client.get(reverse("bookings:room_list"))
        self.assertContains(response, "Room 101")
        self.assertEqual(len(response.context["rooms"]), 2)

    def test_room_detail_and_404(self):
        self.assertContains(self.client.get(f"/rooms/{self.room.pk}/"), "Room 101")
        self.assertEqual(self.client.get("/rooms/999/").status_code, 404)

    def test_the_legacy_link_still_works(self):
        self.assertContains(self.client.get(f"/room-{self.room.pk}/"), "Room 101")

    def test_get_shows_an_empty_form_with_a_csrf_token(self):
        response = self.client.get(reverse("bookings:booking_create"))
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertTemplateUsed(response, "bookings/booking_form.html")

    def test_a_valid_post_saves_and_redirects(self):
        response = self.client.post(reverse("bookings:booking_create"), self.form_data())
        self.assertRedirects(response, reverse("bookings:booking_list"))
        self.assertEqual(Booking.objects.count(), 1)

    def test_an_invalid_post_shows_errors_and_saves_nothing(self):
        response = self.client.post(reverse("bookings:booking_create"), self.form_data(attendees=500))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "seats only 40")
        self.assertEqual(Booking.objects.count(), 0)

    def test_a_post_without_a_csrf_token_is_403(self):
        strict = Client(enforce_csrf_checks=True)
        response = strict.post(reverse("bookings:booking_create"), self.form_data())
        self.assertEqual(response.status_code, 403)

    def test_the_booking_list_shows_bookings(self):
        Booking.objects.create(room=self.room, booked_by="Ana", start=self.start, end=self.end)
        self.assertContains(self.client.get(reverse("bookings:booking_list")), "Ana")


class TemplateTests(DataMixin, TestCase):
    def test_variables_are_escaped_by_default(self):
        out = Template("{{ name }}").render(Context({"name": "<script>alert(1)</script>"}))
        self.assertEqual(out, "&lt;script&gt;alert(1)&lt;/script&gt;")

    def test_a_booked_by_name_with_html_is_escaped_on_the_page(self):
        Booking.objects.create(room=self.room, booked_by="<b>Ana</b>", start=self.start, end=self.end)
        page = self.client.get(reverse("bookings:booking_list")).content.decode()
        self.assertIn("&lt;b&gt;Ana&lt;/b&gt;", page)
        self.assertNotIn("<b>Ana</b>", page)

    def test_pluralize_and_yesno_filters(self):
        page = self.client.get(reverse("bookings:room_list")).content.decode()
        self.assertIn("1 seat)", page)
        self.assertIn("40 seats)", page)

    def test_the_empty_tag_shows_a_message(self):
        Room.objects.all().delete()
        self.assertContains(self.client.get(reverse("bookings:room_list")), "No rooms yet")


class RoutingStillWorksTests(TestCase):
    def test_names_resolve_and_reverse(self):
        self.assertEqual(reverse("bookings:booking_create"), "/bookings/new/")
        self.assertIs(resolve("/bookings/").func, views.booking_list)

    def test_the_admin_lists_rooms_for_a_superuser(self):
        admin = get_user_model().objects.create_superuser("root", "r@example.com", "pw")
        self.client.force_login(admin)
        self.assertEqual(self.client.get("/admin/bookings/room/").status_code, 200)
