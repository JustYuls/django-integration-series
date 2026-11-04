from django.urls import path, re_path

from . import views

app_name = "bookings"  # the namespace: reverse("bookings:room_list")

urlpatterns = [
    path("rooms/", views.RoomListView.as_view(), name="room_list"),
    path("rooms/<int:room_id>/", views.room_detail, name="room_detail"),
    path("calendar/<int:year>/<int:month>/", views.calendar, name="calendar"),
    # An old link style that still works: /room-2/
    re_path(r"^room-(?P<room_id>\d+)/$", views.room_detail, name="room_legacy"),
]
