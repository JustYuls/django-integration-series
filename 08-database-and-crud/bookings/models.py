from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone


class RoomQuerySet(models.QuerySet):
    def with_booking_counts(self):
        return self.annotate(booking_count=Count("bookings"))


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField()
    has_projector = models.BooleanField(default=False)

    objects = RoomQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class BookingQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(end__gte=timezone.now())

    def for_room(self, room):
        return self.filter(room=room)

    def matching(self, text):
        return self.filter(Q(purpose__icontains=text) | Q(booked_by__icontains=text))


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    booked_by = models.CharField(max_length=100)  # becomes a User in Part 11
    purpose = models.CharField(max_length=200, blank=True)
    attendees = models.PositiveIntegerField(default=1)
    start = models.DateTimeField()
    end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BookingQuerySet.as_manager()

    class Meta:
        ordering = ["start"]

    def __str__(self):
        return f"{self.room} for {self.booked_by}"

    def clean(self):
        if self.start and self.end and self.end <= self.start:
            raise ValidationError("A booking must end after it starts.")
