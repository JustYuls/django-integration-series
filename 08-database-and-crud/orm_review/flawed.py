"""A deliberately flawed, AI-style draft of two query helpers (Part 8). Never use this in a real project."""
from bookings.models import Booking


def flawed_booking_lines():
    # FLAW 1: booking.room runs one extra query for every row (the N+1 problem)
    return [f"{booking.room.name}: {booking.booked_by}" for booking in Booking.objects.all()]


def fixed_booking_lines():
    return [f"{booking.room.name}: {booking.booked_by}" for booking in Booking.objects.select_related("room")]


def flawed_busy_check():
    # FLAW 2: len() loads every row just to count them
    return len(Booking.objects.filter(attendees__gte=1)) > 0


def fixed_busy_check():
    return Booking.objects.filter(attendees__gte=1).exists()
