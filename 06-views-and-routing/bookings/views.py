from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from .data import ROOMS, find_room


# Function-based views: a plain function, request in, response out.
def home(request):
    return render(request, "home.html")


@require_GET
def room_detail(request, room_id):
    room = find_room(int(room_id))  # re_path passes text
    if room is None:
        raise Http404("No such room")
    return render(request, "bookings/room_detail.html", {"room": room})


@require_GET
def calendar(request, year, month):
    if not 1 <= month <= 12:
        raise Http404("Month must be 1 to 12")
    return HttpResponse(f"Calendar for {year}-{month:02d}")


# Class-based view: one method per HTTP verb, shared behavior from the base class.
class RoomListView(TemplateView):
    template_name = "bookings/rooms.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rooms"] = ROOMS
        return context
