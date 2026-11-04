"""URL configuration for campus_hub: the project's table of contents."""
from django.contrib import admin
from django.urls import include, path

from bookings import views as bookings_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", bookings_views.home, name="home"),
    path("", include("bookings.urls")),
]
