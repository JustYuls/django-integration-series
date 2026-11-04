from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import Room

FIELDS = ["name", "capacity", "has_projector"]


class RoomListView(ListView):  # public
    model = Room
    template_name = "rooms/room_list.html"
    context_object_name = "rooms"


class RoomDetailView(DetailView):  # public
    model = Room
    template_name = "rooms/room_detail.html"


class RoomCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = "rooms.add_room"  # staff only: anonymous users go to login, others get a 403
    model = Room
    fields = FIELDS
    template_name = "rooms/room_form.html"
    success_url = reverse_lazy("rooms:room_list")
    success_message = "Room created."


class RoomUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = "rooms.change_room"
    model = Room
    fields = FIELDS
    template_name = "rooms/room_form.html"
    success_url = reverse_lazy("rooms:room_list")
    success_message = "Room updated."


class RoomDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "rooms.delete_room"
    model = Room
    template_name = "rooms/room_confirm_delete.html"
    success_url = reverse_lazy("rooms:room_list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:  # something protects this room
            messages.error(self.request, "This room is still in use and cannot be deleted.")
            return redirect(self.success_url)
        messages.success(self.request, "Room deleted.")
        return response
