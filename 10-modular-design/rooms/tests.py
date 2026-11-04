from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking
from rooms.models import Room


class RoomModelTests(TestCase):
    def test_rooms_are_ordered_by_name_and_print_their_name(self):
        Room.objects.create(name="Lab A", capacity=30)
        Room.objects.create(name="Gym", capacity=80)
        self.assertEqual([str(r) for r in Room.objects.all()], ["Gym", "Lab A"])


class RoomViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(name="Room 101", capacity=40, has_projector=True)

    def test_list_shows_rooms(self):
        response = self.client.get(reverse("rooms:room_list"))
        self.assertContains(response, "Room 101")
        self.assertContains(response, "projector")

    def test_the_empty_state(self):
        Room.objects.all().delete()
        self.assertContains(self.client.get(reverse("rooms:room_list")), "No rooms yet")

    def test_detail_and_404(self):
        self.assertContains(self.client.get(reverse("rooms:room_detail", args=[self.room.pk])), "Capacity: 40")
        self.assertEqual(self.client.get(reverse("rooms:room_detail", args=[999])).status_code, 404)

    def test_create(self):
        response = self.client.post(reverse("rooms:room_create"), {"name": "Gym", "capacity": 80}, follow=True)
        self.assertContains(response, "Room created.")
        self.assertTrue(Room.objects.filter(name="Gym").exists())

    def test_create_rejects_a_duplicate_name(self):
        response = self.client.post(reverse("rooms:room_create"), {"name": "Room 101", "capacity": 5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Room.objects.filter(name="Room 101").count(), 1)

    def test_update(self):
        self.client.post(reverse("rooms:room_update", args=[self.room.pk]), {"name": "Room 102", "capacity": 45})
        self.room.refresh_from_db()
        self.assertEqual((self.room.name, self.room.capacity), ("Room 102", 45))

    def test_delete_an_unused_room(self):
        response = self.client.post(reverse("rooms:room_delete", args=[self.room.pk]), follow=True)
        self.assertContains(response, "Room deleted.")
        self.assertFalse(Room.objects.filter(pk=self.room.pk).exists())

    def test_a_room_with_bookings_is_protected_from_deletion(self):
        start = timezone.now() + timedelta(days=1)
        Booking.objects.create(room=self.room, booked_by="Ana", start=start, end=start + timedelta(hours=1))
        response = self.client.post(reverse("rooms:room_delete", args=[self.room.pk]), follow=True)
        self.assertContains(response, "still in use")
        self.assertTrue(Room.objects.filter(pk=self.room.pk).exists())
        self.assertEqual(Booking.objects.count(), 1)
