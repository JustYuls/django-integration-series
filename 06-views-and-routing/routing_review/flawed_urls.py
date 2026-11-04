"""A deliberately flawed project urls.py (Part 6). Never use this in a real project."""
from django.urls import include, path

from bookings import views

urlpatterns = [
    path("", views.home, name="home"),
    path("<str:page>/", views.home, name="page"),  # BUG 2: catch-all, too early
    path("", include("routing_review.flawed_app_urls")),
]
