from django.urls import path, re_path

from . import views

app_name = "bookings"

urlpatterns = [
    path("rooms/", views.RoomListView.as_view(), name="room_list"),
    path("rooms/<int:room_id>/", views.room_detail, name="room_detail"),
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/new/", views.booking_create, name="booking_create"),
    path("calendar/<int:year>/<int:month>/", views.calendar, name="calendar"),
    re_path(r"^room-(?P<room_id>\d+)/$", views.room_detail, name="room_legacy"),
]
