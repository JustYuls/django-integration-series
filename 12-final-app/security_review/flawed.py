"""A deliberately flawed, AI-style draft (Part 11). Never use any of this in a real project."""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from bookings.models import Booking

# FLAW 2: accepts any Host header. manage.py check --deploy does not complain about this.
FLAWED_ALLOWED_HOSTS = ["*"]

# FLAW 3: "security" by hiding a link. Only staff see the button, but the URL itself is open to everyone logged in.
FLAWED_TEMPLATE = '{% if user.is_staff %}<a href="/flawed/cancel/1/">Cancel</a>{% endif %}'


@login_required
def flawed_booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)  # FLAW 1: no ownership check: any logged-in user can cancel any booking
    if request.method == "POST":
        booking.delete()
        return redirect("home")
    return HttpResponse("Cancel this booking?")
