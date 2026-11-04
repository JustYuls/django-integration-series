from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.roles import STAFF, STUDENT
from bookings import services
from bookings.forms import LOCAL_FORMAT, BookingForm
from bookings.models import Booking
from rooms.models import Room

User = get_user_model()


def local(dt):
    return timezone.localtime(dt).strftime(LOCAL_FORMAT)


class DataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(name="Room 101", capacity=40)
        cls.lab = Room.objects.create(name="Lab A", capacity=30)
        cls.ana = User.objects.create_user("ana", "ana@example.com", "x", first_name="Ana", last_name="Cruz")
        cls.ben = User.objects.create_user("ben", "ben@example.com", "x")
        cls.staff = User.objects.create_user("staff", "staff@example.com", "x")
        cls.ana.groups.add(Group.objects.get(name=STUDENT))
        cls.ben.groups.add(Group.objects.get(name=STUDENT))
        cls.staff.groups.add(Group.objects.get(name=STAFF))
        cls.start = timezone.now() + timedelta(days=2)
        cls.end = cls.start + timedelta(hours=2)

    def make_booking(self, owner=None, room=None, days=2, purpose="Review"):
        owner = owner or self.ana
        start = timezone.now() + timedelta(days=days)
        return Booking.objects.create(room=room or self.room, owner=owner, booked_by=owner.get_username(), booker_email=owner.email,
                                      purpose=purpose, start=start, end=start + timedelta(hours=2))

    def form_data(self, **changes):
        data = {"room": self.room.pk, "purpose": "Review", "attendees": 10, "start": local(self.start), "end": local(self.end)}
        data.update(changes)
        return data


class ModelAndFormTests(DataMixin, TestCase):
    def test_a_booking_must_end_after_it_starts(self):
        with self.assertRaises(ValidationError):
            Booking(room=self.room, owner=self.ana, booked_by="ana", start=self.end, end=self.start).full_clean()

    def test_the_form_has_no_owner_field(self):
        self.assertNotIn("owner", BookingForm().fields)

    def test_over_capacity_double_booking_and_self_edit(self):
        self.assertIn("attendees", BookingForm(self.form_data(attendees=99)).errors)
        booking = Booking.objects.create(room=self.room, owner=self.ana, booked_by="ana", start=self.start, end=self.end)
        self.assertFalse(BookingForm(self.form_data()).is_valid())
        self.assertTrue(BookingForm(self.form_data(), instance=booking).is_valid())

    @override_settings(HOLIDAYS_ENABLED=True)
    def test_a_holiday_is_rejected(self):
        with mock.patch("bookings.forms.holiday_on", return_value="Rizal Day"):
            form = BookingForm(self.form_data())
            errors = form.errors
        self.assertIn("public holiday: Rizal Day", errors["start"][0])


class ServiceTests(DataMixin, TestCase):
    def test_the_service_sets_the_owner_from_the_user_not_from_the_form(self):
        form = BookingForm(self.form_data())
        self.assertTrue(form.is_valid())
        booking = services.book_room(form, self.ana)
        self.assertEqual((booking.owner, booking.booked_by, booking.booker_email), (self.ana, "Ana Cruz", "ana@example.com"))
        self.assertEqual(mail.outbox[0].to, ["ana@example.com"])

    def test_a_mail_failure_never_undoes_a_saved_booking(self):
        form = BookingForm(self.form_data())
        form.is_valid()
        with mock.patch("bookings.services.send_booking_confirmation", side_effect=RuntimeError("smtp down")):
            with self.assertLogs("bookings.services", level="ERROR"):
                services.book_room(form, self.ana)
        self.assertEqual(Booking.objects.count(), 1)


class AuthenticationRequiredTests(DataMixin, TestCase):
    def test_anonymous_visitors_are_redirected_to_login(self):
        booking = self.make_booking()
        for name, args in [("booking_list", []), ("booking_create", []), ("booking_update", [booking.pk]), ("booking_delete", [booking.pk]), ("room_schedule", [self.room.pk])]:
            url = reverse(f"bookings:{name}", args=args)
            self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}", fetch_redirect_response=False, msg_prefix=name)

    def test_a_user_without_the_add_permission_gets_a_403(self):
        outsider = User.objects.create_user("outsider", "o@example.com", "x")
        self.client.force_login(outsider)
        self.assertEqual(self.client.get(reverse("bookings:booking_create")).status_code, 403)


class OwnershipTests(DataMixin, TestCase):
    def test_a_student_creates_a_booking_that_belongs_to_them(self):
        self.client.force_login(self.ana)
        response = self.client.post(reverse("bookings:booking_create"), self.form_data(), follow=True)
        self.assertContains(response, "Booking saved.")
        self.assertEqual(Booking.objects.get().owner, self.ana)
        self.assertEqual(len(mail.outbox), 1)

    def test_a_posted_owner_field_is_ignored(self):
        self.client.force_login(self.ana)
        self.client.post(reverse("bookings:booking_create"), self.form_data(owner=self.ben.pk, booked_by="Someone Else"))
        booking = Booking.objects.get()
        self.assertEqual(booking.owner, self.ana)
        self.assertNotEqual(booking.booked_by, "Someone Else")

    def test_a_student_sees_only_their_own_bookings(self):
        mine, theirs = self.make_booking(self.ana, purpose="mine"), self.make_booking(self.ben, purpose="theirs", days=4)
        self.client.force_login(self.ana)
        page = self.client.get(reverse("bookings:booking_list"))
        self.assertEqual([b.pk for b in page.context["page"]], [mine.pk])
        self.assertNotContains(page, "theirs")

    def test_a_student_cannot_open_edit_or_delete_someone_elses_booking(self):
        theirs = self.make_booking(self.ben)
        self.client.force_login(self.ana)
        self.assertEqual(self.client.get(reverse("bookings:booking_update", args=[theirs.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("bookings:booking_delete", args=[theirs.pk])).status_code, 404)
        self.assertTrue(Booking.objects.filter(pk=theirs.pk).exists())

    def test_the_owner_can_edit_and_delete(self):
        mine = self.make_booking(self.ana)
        self.client.force_login(self.ana)
        data = self.form_data(purpose="Changed", start=local(mine.start), end=local(mine.end))
        self.client.post(reverse("bookings:booking_update", args=[mine.pk]), data)
        mine.refresh_from_db()
        self.assertEqual(mine.purpose, "Changed")
        self.client.post(reverse("bookings:booking_delete", args=[mine.pk]))
        self.assertFalse(Booking.objects.filter(pk=mine.pk).exists())

    def test_staff_see_and_manage_every_booking(self):
        theirs = self.make_booking(self.ben)
        self.client.force_login(self.staff)
        self.assertEqual(len(self.client.get(reverse("bookings:booking_list")).context["page"]), 1)
        self.assertEqual(self.client.get(reverse("bookings:booking_update", args=[theirs.pk])).status_code, 200)
        self.client.post(reverse("bookings:booking_delete", args=[theirs.pk]))
        self.assertEqual(Booking.objects.count(), 0)

    def test_visible_to_for_anonymous_users_is_empty(self):
        self.make_booking()
        from django.contrib.auth.models import AnonymousUser
        self.assertEqual(Booking.objects.visible_to(AnonymousUser()).count(), 0)

    def test_the_schedule_shows_names_only_to_staff(self):
        self.make_booking(self.ben)
        self.client.force_login(self.ana)
        self.assertNotContains(self.client.get(reverse("bookings:room_schedule", args=[self.room.pk])), "ben")
        self.client.force_login(self.staff)
        self.assertContains(self.client.get(reverse("bookings:room_schedule", args=[self.room.pk])), "ben")


class ListAndCsrfTests(DataMixin, TestCase):
    def test_filters_search_pagination_and_query_count(self):
        for d in range(2, 9):
            self.make_booking(days=d, purpose="Review" if d % 2 else "Workshop")
        self.client.force_login(self.ana)
        url = reverse("bookings:booking_list")
        self.assertEqual(self.client.get(url).context["page"].paginator.num_pages, 2)
        self.assertEqual(self.client.get(url, {"q": "workshop"}).context["page"].paginator.count, 4)
        self.assertEqual(self.client.get(url, {"room": "x'; DROP"}).status_code, 200)
        with self.assertNumQueries(7):  # session, user, 2 for permissions, rooms for the filter, the paginator count, the page
            self.client.get(url)

    def test_a_post_without_a_csrf_token_is_403(self):
        booking = self.make_booking()
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.ana)
        self.assertEqual(strict.post(reverse("bookings:booking_delete", args=[booking.pk])).status_code, 403)
        self.assertTrue(Booking.objects.filter(pk=booking.pk).exists())
