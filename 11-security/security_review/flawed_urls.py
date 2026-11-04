"""URLs for the flawed draft only (Part 11)."""
from django.urls import path

from campus_hub import views
from security_review.flawed import flawed_booking_cancel

urlpatterns = [
    path("", views.home, name="home"),
    path("flawed/cancel/<int:pk>/", flawed_booking_cancel),
]
