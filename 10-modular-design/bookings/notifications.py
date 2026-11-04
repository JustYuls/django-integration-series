from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


def send_booking_confirmation(booking):
    """E-mail the booker. Returns how many messages were sent (0 when no address was given)."""
    if not booking.booker_email:
        return 0
    start = timezone.localtime(booking.start)
    end = timezone.localtime(booking.end)
    body = (
        f"Hi {booking.booked_by},\n\n"
        f"Your booking is confirmed.\n"
        f"Room: {booking.room.name}\n"
        f"When: {start:%b %d, %Y %I:%M %p} to {end:%I:%M %p}\n"
    )
    subject = f"Booking confirmed: {booking.room.name}"
    return send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [booking.booker_email])
