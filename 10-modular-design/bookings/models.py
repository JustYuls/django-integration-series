from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class BookingQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(end__gte=timezone.now())

    def matching(self, text):
        return self.filter(Q(purpose__icontains=text) | Q(booked_by__icontains=text))


class Booking(models.Model):
    """A booking depends on rooms (one direction only). PROTECT: a room with bookings cannot be deleted."""

    room = models.ForeignKey("rooms.Room", on_delete=models.PROTECT, related_name="bookings")
    booked_by = models.CharField(max_length=100)  # becomes a User in Part 11
    booker_email = models.EmailField(blank=True)
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
