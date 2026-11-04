from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from .forms import BookingForm
from .models import Booking, Room


def home(request):
    return render(request, "home.html")


@require_GET
def room_detail(request, room_id):
    room = get_object_or_404(Room, pk=room_id)  # a 404 page if there is no such room
    return render(request, "bookings/room_detail.html", {"room": room, "bookings": room.bookings.all()})


@require_GET
def calendar(request, year, month):
    if not 1 <= month <= 12:
        raise Http404("Month must be 1 to 12")
    return HttpResponse(f"Calendar for {year}-{month:02d}")


class RoomListView(TemplateView):
    template_name = "bookings/rooms.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rooms"] = Room.objects.all()
        return context


@require_GET
def booking_list(request):
    return render(request, "bookings/booking_list.html", {"bookings": Booking.objects.select_related("room")})


def booking_create(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("bookings:booking_list")  # Post/Redirect/Get: a refresh will not re-submit
    else:
        form = BookingForm()
    return render(request, "bookings/booking_form.html", {"form": form})
