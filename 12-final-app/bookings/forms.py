from django import forms
from django.conf import settings
from django.utils import timezone

from holiday_api.client import holiday_on

from .models import Booking

LOCAL_FORMAT = "%Y-%m-%dT%H:%M"  # what <input type="datetime-local"> sends


class AvailabilityForm(forms.Form):
    """Search for a free room: no data is saved, so it is a plain Form."""

    start = forms.DateTimeField(input_formats=[LOCAL_FORMAT], widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format=LOCAL_FORMAT))
    end = forms.DateTimeField(input_formats=[LOCAL_FORMAT], widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format=LOCAL_FORMAT))
    attendees = forms.IntegerField(min_value=1, initial=1)

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start"), cleaned.get("end")
        if start and end and end <= start:
            self.add_error("end", "The end must be after the start.")
        return cleaned


class BookingForm(forms.ModelForm):
    """The form has no owner field: the owner is the logged-in user, set by the service."""

    class Meta:
        model = Booking
        fields = ["room", "purpose", "attendees", "start", "end"]
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
        if start and settings.HOLIDAYS_ENABLED and not self.errors:
            day = timezone.localtime(start).date()
            holiday = holiday_on(day, settings.HOLIDAY_COUNTRY)
            if holiday:
                self.add_error("start", f"That day is a public holiday: {holiday}.")
        if room and start and end and not self.errors:
            others = Booking.objects.filter(room=room, start__lt=end, end__gt=start)
            if self.instance.pk:
                others = others.exclude(pk=self.instance.pk)
            if others.exists():
                raise forms.ValidationError("That room is already booked at that time.")
        return cleaned
