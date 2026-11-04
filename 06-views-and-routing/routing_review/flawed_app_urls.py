"""A deliberately flawed copy of bookings/urls.py (Part 6). Never use this in a real project."""
from django.urls import path, re_path

from bookings import views

# BUG 1: no app_name here, so there is no "bookings" namespace
urlpatterns = [
    path("rooms/", views.RoomListView.as_view(), name="room_list"),
    path("rooms/<int:room_id>/", views.room_detail, name="room_detail"),
    # BUG 3: no ^ and $ anchors
    re_path(r"room-(?P<room_id>\d+)", views.room_detail, name="room_legacy"),
]
