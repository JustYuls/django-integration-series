from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET, require_http_methods
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from .forms import BookingForm
from .models import Booking, Room

PER_PAGE = 5


def home(request):
    return render(request, "home.html")


@require_GET
def calendar(request, year, month):
    if not 1 <= month <= 12:
        raise Http404("Month must be 1 to 12")
    return HttpResponse(f"Calendar for {year}-{month:02d}")


# ---- Rooms: CRUD with Django's generic class-based views ----
class RoomListView(TemplateView):
    template_name = "bookings/rooms.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rooms"] = Room.objects.with_booking_counts()
        return context


@require_GET
def room_detail(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    return render(request, "bookings/room_detail.html", {"room": room, "bookings": room.bookings.all()})


class RoomCreateView(SuccessMessageMixin, CreateView):
    model = Room
    fields = ["name", "capacity", "has_projector"]
    template_name = "bookings/room_form.html"
    success_url = reverse_lazy("bookings:room_list")
    success_message = "Room created."


class RoomUpdateView(SuccessMessageMixin, UpdateView):
    model = Room
    fields = ["name", "capacity", "has_projector"]
    template_name = "bookings/room_form.html"
    success_url = reverse_lazy("bookings:room_list")
    success_message = "Room updated."


class RoomDeleteView(DeleteView):
    model = Room
    template_name = "bookings/room_confirm_delete.html"
    success_url = reverse_lazy("bookings:room_list")

    def form_valid(self, form):
        messages.success(self.request, "Room deleted.")
        return super().form_valid(form)


# ---- Bookings: CRUD with function-based views ----
@require_GET
def booking_list(request):
    bookings = Booking.objects.select_related("room")  # one JOIN instead of one query per row
    room_id = request.GET.get("room", "")
    text = request.GET.get("q", "").strip()
    if room_id.isdigit():
        bookings = bookings.filter(room_id=int(room_id))
    if text:
        bookings = bookings.matching(text)
    page = Paginator(bookings, PER_PAGE).get_page(request.GET.get("page"))
    context = {"page": page, "rooms": Room.objects.all(), "selected_room": room_id, "q": text}
    return render(request, "bookings/booking_list.html", context)


def booking_create(request):
    form = BookingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
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
    if request.method == "POST":  # a GET only asks "are you sure?"
        booking.delete()
        messages.success(request, "Booking deleted.")
        return redirect("bookings:booking_list")
    return render(request, "bookings/booking_confirm_delete.html", {"booking": booking})
