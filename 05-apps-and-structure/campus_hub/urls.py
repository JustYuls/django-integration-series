"""URL configuration for campus_hub.

TemplateView shows a template without writing a view. We write real views in Part 6.
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html')),
    path('rooms/', TemplateView.as_view(template_name='bookings/rooms.html')),
]
