from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from rooms.models import Room

from . import services
from .availability import available_rooms
from .forms import AvailabilityForm, BookingForm
from .models import Booking

PER_PAGE = 5


@login_required
@require_GET
def booking_list(request):
    bookings = Booking.objects.visible_to(request.user).select_related("room")  # authorization: only what this user may see
    room_id = request.GET.get("room", "")
    text = request.GET.get("q", "").strip()
    if room_id.isdigit():
        bookings = bookings.filter(room_id=int(room_id))
    if text:
        bookings = bookings.matching(text)
    page = Paginator(bookings, PER_PAGE).get_page(request.GET.get("page"))
    context = {"page": page, "rooms": Room.objects.all(), "selected_room": room_id, "q": text}
    return render(request, "bookings/booking_list.html", context)


@login_required
@require_GET
def find_room(request):
    form = AvailabilityForm(request.GET or None)
    rooms = None
    if request.GET and form.is_valid():  # a GET form: the search can be bookmarked and shared
        data = form.cleaned_data
        rooms = available_rooms(data["start"], data["end"], data["attendees"])
    return render(request, "bookings/find_room.html", {"form": form, "rooms": rooms})


@login_required
@require_GET
def room_schedule(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    return render(request, "bookings/room_schedule.html", {"room": room, "bookings": room.bookings.upcoming()})


@login_required
@permission_required("bookings.add_booking", raise_exception=True)  # logged in, and allowed to add: a 403 otherwise
def booking_create(request):
    form = BookingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        services.book_room(form, request.user)
        messages.success(request, "Booking saved.")
        return redirect("bookings:booking_list")
    return render(request, "bookings/booking_form.html", {"form": form, "title": "New booking"})


@login_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking.objects.visible_to(request.user), pk=pk)  # not yours: 404, as if it did not exist
    form = BookingForm(request.POST or None, instance=booking)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Booking updated.")
        return redirect("bookings:booking_list")
    return render(request, "bookings/booking_form.html", {"form": form, "title": "Edit booking"})


@login_required
@require_http_methods(["GET", "POST"])
def booking_delete(request, pk):
    booking = get_object_or_404(Booking.objects.visible_to(request.user), pk=pk)
    if request.method == "POST":
        services.cancel_booking(booking)
        messages.success(request, "Booking deleted.")
        return redirect("bookings:booking_list")
    return render(request, "bookings/booking_confirm_delete.html", {"booking": booking})
