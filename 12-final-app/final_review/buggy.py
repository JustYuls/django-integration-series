"""The first version of "find a free room" that a bug report was filed against (Part 12). Never use it."""
from rooms.models import Room


def buggy_available_rooms(start, end, attendees=1):
    # BUG: two conditions inside one exclude() on a multi-valued relation. Django may satisfy each
    # condition with a DIFFERENT booking, so a room with an early and a late booking looks busy all day.
    return Room.objects.filter(capacity__gte=attendees).exclude(bookings__start__lt=end, bookings__end__gt=start)
