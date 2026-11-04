from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.roles import STAFF, STUDENT
from bookings.models import Booking
from rooms.models import Room

User = get_user_model()


class Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(name="Room 101", capacity=40, has_projector=True)
        cls.student = User.objects.create_user("student", "s@example.com", "x")
        cls.student.groups.add(Group.objects.get(name=STUDENT))
        cls.staff = User.objects.create_user("staff", "t@example.com", "x")
        cls.staff.groups.add(Group.objects.get(name=STAFF))


class PublicTests(Base):
    def test_anyone_can_read_the_list_and_a_room(self):
        self.assertContains(self.client.get(reverse("rooms:room_list")), "Room 101")
        self.assertContains(self.client.get(reverse("rooms:room_detail", args=[self.room.pk])), "Capacity: 40")

    def test_the_empty_state_and_404(self):
        self.assertEqual(self.client.get(reverse("rooms:room_detail", args=[999])).status_code, 404)

    def test_management_links_are_hidden_from_anonymous_visitors_and_students(self):
        self.assertNotContains(self.client.get(reverse("rooms:room_list")), "Add a room")
        self.client.force_login(self.student)
        self.assertNotContains(self.client.get(reverse("rooms:room_list")), "Add a room")

    def test_staff_see_the_management_links(self):
        self.client.force_login(self.staff)
        self.assertContains(self.client.get(reverse("rooms:room_list")), "Add a room")


class AuthorizationTests(Base):
    def urls(self):
        return [reverse("rooms:room_create"), reverse("rooms:room_update", args=[self.room.pk]), reverse("rooms:room_delete", args=[self.room.pk])]

    def test_anonymous_users_are_sent_to_the_login_page(self):
        for url in self.urls():
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('login')}?next={url}", fetch_redirect_response=False)

    def test_students_get_a_403_even_on_the_direct_url(self):
        self.client.force_login(self.student)
        for url in self.urls():
            self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(reverse("rooms:room_delete", args=[self.room.pk])).status_code, 403)
        self.assertTrue(Room.objects.filter(pk=self.room.pk).exists())

    def test_staff_can_create_update_and_delete(self):
        self.client.force_login(self.staff)
        self.client.post(reverse("rooms:room_create"), {"name": "Gym", "capacity": 80})
        gym = Room.objects.get(name="Gym")
        self.client.post(reverse("rooms:room_update", args=[gym.pk]), {"name": "Big Gym", "capacity": 90})
        gym.refresh_from_db()
        self.assertEqual(gym.name, "Big Gym")
        self.client.post(reverse("rooms:room_delete", args=[gym.pk]))
        self.assertFalse(Room.objects.filter(pk=gym.pk).exists())

    def test_a_room_with_bookings_is_protected_even_from_staff(self):
        start = timezone.now() + timedelta(days=1)
        Booking.objects.create(room=self.room, owner=self.student, booked_by="s", start=start, end=start + timedelta(hours=1))
        self.client.force_login(self.staff)
        response = self.client.post(reverse("rooms:room_delete", args=[self.room.pk]), follow=True)
        self.assertContains(response, "still in use")
        self.assertTrue(Room.objects.filter(pk=self.room.pk).exists())
