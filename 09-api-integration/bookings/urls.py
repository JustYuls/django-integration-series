from django.urls import path, re_path

from . import views

app_name = "bookings"

urlpatterns = [
    path("rooms/", views.RoomListView.as_view(), name="room_list"),
    path("rooms/new/", views.RoomCreateView.as_view(), name="room_create"),
    path("rooms/<int:room_id>/", views.room_detail, name="room_detail"),
    path("rooms/<int:pk>/edit/", views.RoomUpdateView.as_view(), name="room_update"),
    path("rooms/<int:pk>/delete/", views.RoomDeleteView.as_view(), name="room_delete"),
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/new/", views.booking_create, name="booking_create"),
    path("bookings/<int:pk>/edit/", views.booking_update, name="booking_update"),
    path("bookings/<int:pk>/delete/", views.booking_delete, name="booking_delete"),
    path("holidays/<int:year>/", views.holiday_list, name="holiday_list"),
    path("calendar/<int:year>/<int:month>/", views.calendar, name="calendar"),
    re_path(r"^room-(?P<room_id>\d+)/$", views.room_detail, name="room_legacy"),
]
