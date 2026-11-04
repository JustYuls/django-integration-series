from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.booking_list, name="booking_list"),
    path("new/", views.booking_create, name="booking_create"),
    path("<int:pk>/edit/", views.booking_update, name="booking_update"),
    path("<int:pk>/delete/", views.booking_delete, name="booking_delete"),
    path("room/<int:room_id>/", views.room_schedule, name="room_schedule"),
]
