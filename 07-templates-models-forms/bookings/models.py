from django.core.exceptions import ValidationError
from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField()
    has_projector = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    booked_by = models.CharField(max_length=100)  # becomes a User in Part 11
    purpose = models.CharField(max_length=200, blank=True)
    attendees = models.PositiveIntegerField(default=1)
    start = models.DateTimeField()
    end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start"]

    def __str__(self):
        return f"{self.room} for {self.booked_by}"

    def clean(self):
        # Model-level rule: runs in the admin and in ModelForms.
        if self.start and self.end and self.end <= self.start:
            raise ValidationError("A booking must end after it starts.")
