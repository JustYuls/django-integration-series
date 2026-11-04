from django import forms
from django.utils import timezone

from .models import Booking

LOCAL_FORMAT = "%Y-%m-%dT%H:%M"  # what <input type="datetime-local"> sends


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["room", "booked_by", "purpose", "attendees", "start", "end"]
        widgets = {
            "start": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=LOCAL_FORMAT),
            "end": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=LOCAL_FORMAT),
        }

    def clean(self):
        cleaned = super().clean()
        room, start, end = cleaned.get("room"), cleaned.get("start"), cleaned.get("end")
        attendees = cleaned.get("attendees")
        if start and start < timezone.now() and not self.instance.pk:
            self.add_error("start", "The start cannot be in the past.")
        if room and attendees and attendees > room.capacity:
            self.add_error("attendees", f"{room.name} seats only {room.capacity}.")
        if room and start and end and not self.errors:
            others = Booking.objects.filter(room=room, start__lt=end, end__gt=start)
            if self.instance.pk:
                others = others.exclude(pk=self.instance.pk)  # editing must not clash with itself
            if others.exists():
                raise forms.ValidationError("That room is already booked at that time.")
        return cleaned
