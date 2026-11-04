from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from rooms.models import Room

from . import services
from .forms import BookingForm
from .models import Booking

PER_PAGE = 5


@require_GET
def booking_list(request):
    bookings = Booking.objects.select_related("room")
    room_id = request.GET.get("room", "")
    text = request.GET.get("q", "").strip()
    if room_id.isdigit():
        bookings = bookings.filter(room_id=int(room_id))
    if text:
        bookings = bookings.matching(text)
    page = Paginator(bookings, PER_PAGE).get_page(request.GET.get("page"))
    context = {"page": page, "rooms": Room.objects.all(), "selected_room": room_id, "q": text}
    return render(request, "bookings/booking_list.html", context)


@require_GET
def room_schedule(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    return render(request, "bookings/room_schedule.html", {"room": room, "bookings": room.bookings.upcoming()})


def booking_create(request):
    form = BookingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        services.book_room(form)  # all the workflow lives in the service
        messages.success(request, "Booking saved.")
        return redirect("bookings:booking_list")
    return render(request, "bookings/booking_form.html", {"form": form, "title": "New booking"})


def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    form = BookingForm(request.POST or None, instance=booking)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Booking updated.")
        return redirect("bookings:booking_list")
    return render(request, "bookings/booking_form.html", {"form": form, "title": "Edit booking"})


@require_http_methods(["GET", "POST"])
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == "POST":
        services.cancel_booking(booking)
        messages.success(request, "Booking deleted.")
        return redirect("bookings:booking_list")
    return render(request, "bookings/booking_confirm_delete.html", {"booking": booking})
