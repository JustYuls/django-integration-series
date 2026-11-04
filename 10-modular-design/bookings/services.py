"""The workflows of the booking app. Views stay thin: they read the request and call a service."""
import logging

from .notifications import send_booking_confirmation

log = logging.getLogger(__name__)


def book_room(form):
    """Save a validated booking form, then notify. A mail problem must never undo or hide a saved booking."""
    booking = form.save()
    try:
        send_booking_confirmation(booking)
    except Exception:  # noqa: BLE001
        log.exception("Could not send the confirmation for booking %s", booking.pk)
    return booking


def cancel_booking(booking):
    booking.delete()
