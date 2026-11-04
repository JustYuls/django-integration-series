from django.urls import include, path

from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("", include("django.contrib.auth.urls")),  # login, logout, password change and reset
]
