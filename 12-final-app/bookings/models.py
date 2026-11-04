from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

MANAGE_ALL = "bookings.manage_all_bookings"


class BookingQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(end__gte=timezone.now())

    def matching(self, text):
        return self.filter(Q(purpose__icontains=text) | Q(booked_by__icontains=text))

    def visible_to(self, user):
        """The authorization rule in one place: managers see everything, everyone else only their own."""
        if user.is_authenticated and user.has_perm(MANAGE_ALL):
            return self
        if user.is_authenticated:
            return self.filter(owner=user)
        return self.none()


class Booking(models.Model):
    """A booking depends on rooms (one direction only). PROTECT: a room with bookings cannot be deleted."""

    room = models.ForeignKey("rooms.Room", on_delete=models.PROTECT, related_name="bookings")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="bookings")
    booked_by = models.CharField(max_length=100)  # the owner's name when the booking was made
    booker_email = models.EmailField(blank=True)
    purpose = models.CharField(max_length=200, blank=True)
    attendees = models.PositiveIntegerField(default=1)
    start = models.DateTimeField()
    end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BookingQuerySet.as_manager()

    class Meta:
        ordering = ["start"]
        permissions = [("manage_all_bookings", "Can see and change every booking")]
        # Measured in Part 12: makes "is this room free?" a covering-index search (see final_review/perf.py)
        indexes = [models.Index(fields=["room", "start", "end"], name="booking_room_start_end_idx")]

    def __str__(self):
        return f"{self.room} for {self.booked_by}"

    def clean(self):
        if self.start and self.end and self.end <= self.start:
            raise ValidationError("A booking must end after it starts.")
