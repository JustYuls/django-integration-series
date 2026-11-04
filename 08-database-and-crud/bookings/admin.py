from django.contrib import admin

from .models import Booking, Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "has_projector")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("room", "booked_by", "start", "end", "attendees")
