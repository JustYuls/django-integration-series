"""Part 12 tests: finding a free room, the index, and the demo data command."""
from datetime import datetime, timedelta, timezone as dt_timezone
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.roles import STUDENT
from bookings.availability import available_rooms
from bookings.forms import LOCAL_FORMAT, AvailabilityForm
from bookings.models import Booking
from rooms.models import Room

User = get_user_model()


def at(hour, day=1):
    return datetime(2027, 3, day, hour, 0, tzinfo=dt_timezone.utc)


class AvailabilityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.a = Room.objects.create(name="Room A", capacity=40)
        cls.c = Room.objects.create(name="Lab C", capacity=10)
        cls.gym = Room.objects.create(name="Gym", capacity=80)
        for room, s, e in [(cls.a, 9, 11), (cls.c, 8, 9), (cls.c, 13, 14)]:
            Booking.objects.create(room=room, booked_by="x", start=at(s), end=at(e))

    def names(self, *args, **kwargs):
        return sorted(r.name for r in available_rooms(*args, **kwargs))

    def test_a_room_with_an_early_and_a_late_booking_is_free_in_between(self):
        self.assertEqual(self.names(at(10), at(12)), ["Gym", "Lab C"])  # the bug report: Lab C used to be missing

    def test_overlapping_rooms_are_excluded(self):
        self.assertEqual(self.names(at(10), at(12)).count("Room A"), 0)

    def test_back_to_back_bookings_do_not_clash(self):
        self.assertIn("Room A", self.names(at(11), at(12)))  # Room A's booking ends exactly at 11:00
        self.assertIn("Room A", self.names(at(7), at(9)))     # and starts exactly at 09:00

    def test_a_booking_inside_the_window_blocks_the_room(self):
        self.assertNotIn("Lab C", self.names(at(7), at(15)))

    def test_capacity_filters_rooms(self):
        self.assertEqual(self.names(at(10), at(12), attendees=50), ["Gym"])

    def test_it_is_one_query(self):
        with self.assertNumQueries(1):
            list(available_rooms(at(10), at(12)))


class AvailabilityFormTests(TestCase):
    def data(self, **changes):
        data = {"start": "2027-03-01T10:00", "end": "2027-03-01T12:00", "attendees": 5}
        data.update(changes)
        return data

    def test_valid(self):
        self.assertTrue(AvailabilityForm(self.data()).is_valid())

    def test_end_must_be_after_start(self):
        self.assertIn("end", AvailabilityForm(self.data(end="2027-03-01T09:00")).errors)

    def test_attendees_must_be_positive(self):
        self.assertIn("attendees", AvailabilityForm(self.data(attendees=0)).errors)


class FindRoomViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("ana", "ana@example.com", "x")
        cls.user.groups.add(Group.objects.get(name=STUDENT))
        cls.room = Room.objects.create(name="Room 101", capacity=40)

    def window(self, days=3, hours=2):
        start = timezone.now() + timedelta(days=days)
        return {"start": timezone.localtime(start).strftime(LOCAL_FORMAT), "end": timezone.localtime(start + timedelta(hours=hours)).strftime(LOCAL_FORMAT), "attendees": 5}

    def test_the_page_needs_a_login(self):
        url = reverse("bookings:find_room")
        self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}", fetch_redirect_response=False)

    def test_the_empty_form_shows_no_results(self):
        self.client.force_login(self.user)
        self.assertNotContains(self.client.get(reverse("bookings:find_room")), "Free rooms")

    def test_a_search_lists_the_free_rooms(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("bookings:find_room"), self.window())
        self.assertContains(response, "Room 101")

    def test_a_search_with_no_free_room_says_so(self):
        window = self.window()
        start = timezone.make_aware(datetime.strptime(window["start"], LOCAL_FORMAT))
        Booking.objects.create(room=self.room, booked_by="x", start=start, end=start + timedelta(hours=2))
        self.client.force_login(self.user)
        self.assertContains(self.client.get(reverse("bookings:find_room"), window), "No room is free")

    def test_a_bad_window_shows_an_error_not_results(self):
        self.client.force_login(self.user)
        window = self.window()
        window["end"] = window["start"]
        response = self.client.get(reverse("bookings:find_room"), window)
        self.assertContains(response, "The end must be after the start.")
        self.assertNotContains(response, "Free rooms")


class IndexTests(TestCase):
    def test_the_composite_index_exists_in_the_database(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='bookings_booking'")
            names = [row[0] for row in cursor.fetchall()]
        self.assertIn("booking_room_start_end_idx", names)

    def test_the_index_is_declared_on_the_model(self):
        self.assertIn("booking_room_start_end_idx", [i.name for i in Booking._meta.indexes])


class SeedDemoTests(TestCase):
    def run_command(self):
        out = StringIO()
        call_command("seed_demo", stdout=out)
        return out.getvalue()

    def test_it_creates_rooms_users_roles_and_a_booking(self):
        output = self.run_command()
        self.assertEqual(Room.objects.count(), 3)
        self.assertTrue(User.objects.get(username="demo_student").groups.filter(name="Student").exists())
        self.assertTrue(User.objects.get(username="demo_staff").groups.filter(name="Staff").exists())
        self.assertEqual(Booking.objects.count(), 1)
        self.assertIn("Password:", output)

    def test_the_passwords_are_random_and_stored_hashed(self):
        output = self.run_command()
        student = User.objects.get(username="demo_student")
        password = [line for line in output.splitlines() if line.startswith("Created demo_student")][0].split("Password: ")[1]
        self.assertTrue(student.check_password(password))
        self.assertNotEqual(student.password, password)

    def test_running_it_again_changes_nothing(self):
        self.run_command()
        before = User.objects.get(username="demo_student").password
        output = self.run_command()
        self.assertIn("already exists", output)
        self.assertEqual(User.objects.get(username="demo_student").password, before)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(Room.objects.count(), 3)
