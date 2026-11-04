"""Find rooms that are free for a time window."""
from django.db.models import Exists, OuterRef

from rooms.models import Room

from .models import Booking


def available_rooms(start, end, attendees=1):
    """Rooms that fit the group and have no booking overlapping [start, end).

    One correlated EXISTS: each booking is tested against BOTH conditions together.
    Back-to-back bookings are fine: a booking that ends exactly at `start` does not clash.
    """
    clash = Booking.objects.filter(room=OuterRef("pk"), start__lt=end, end__gt=start)
    return Room.objects.filter(capacity__gte=attendees).exclude(Exists(clash))
