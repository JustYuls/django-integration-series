"""The workflows of the booking app. Views stay thin: they read the request and call a service."""
import logging

from .notifications import send_booking_confirmation

log = logging.getLogger(__name__)


def book_room(form, user):
    """Save a validated booking for a user, then notify. Who owns it is decided here, never by the browser."""
    booking = form.save(commit=False)
    booking.owner = user
    booking.booked_by = user.get_full_name() or user.get_username()
    booking.booker_email = user.email
    booking.save()
    try:
        send_booking_confirmation(booking)
    except Exception:  # noqa: BLE001
        log.exception("Could not send the confirmation for booking %s", booking.pk)
    return booking


def cancel_booking(booking):
    booking.delete()
