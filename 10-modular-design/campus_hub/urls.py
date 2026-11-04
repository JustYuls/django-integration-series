"""The project's table of contents: each app owns its own routes and namespace."""
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("rooms/", include("rooms.urls")),
    path("bookings/", include("bookings.urls")),
    path("holidays/", include("holiday_api.urls")),
]
