"""Create demo data for the final presentation: rooms, a student, a staff member, and a few bookings."""
import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.roles import STAFF, STUDENT
from bookings.models import Booking
from rooms.models import Room

ROOMS = [("Room 101", 40, True), ("Lab A", 30, False), ("Gym", 80, False)]


class Command(BaseCommand):
    help = "Create demo rooms, users and bookings. Safe to run again: it never overwrites an existing user."

    def handle(self, *args, **options):
        User = get_user_model()
        for name, capacity, projector in ROOMS:
            Room.objects.get_or_create(name=name, defaults={"capacity": capacity, "has_projector": projector})
        users = {}
        for username, role in (("demo_student", STUDENT), ("demo_staff", STAFF)):
            user, created = User.objects.get_or_create(username=username, defaults={"email": f"{username}@example.com"})
            if created:
                password = secrets.token_urlsafe(12)  # random, printed once, never stored in the code
                user.set_password(password)
                user.save()
                user.groups.add(Group.objects.get(name=role))
                self.stdout.write(f"Created {username} ({role}). Password: {password}")
            else:
                self.stdout.write(f"{username} already exists: its password is unchanged.")
            users[username] = user
        student, room = users["demo_student"], Room.objects.get(name="Room 101")
        if not Booking.objects.filter(owner=student).exists():
            start = (timezone.now() + timedelta(days=2)).replace(hour=9, minute=0, second=0, microsecond=0)
            Booking.objects.create(room=room, owner=student, booked_by="demo_student", booker_email=student.email, purpose="Demo review session",
                                   attendees=12, start=start, end=start + timedelta(hours=2))
            self.stdout.write("Created a demo booking.")
        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
