"""A deliberately flawed, AI-style draft of the booking form pieces (Part 7). Never use this in a real project."""
from django import forms

from bookings.models import Booking

# FLAW 1: no {% csrf_token %} inside the form
FLAWED_FORM_TEMPLATE = '<form method="post">{{ form.as_p }}<button>Save</button></form>'

# FLAW 2: |safe on text a user typed
FLAWED_NAME_TEMPLATE = "<p>Booked by {{ name|safe }}</p>"


# FLAW 3: no clean(), so capacity and double bookings are never checked
class FlawedBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["room", "booked_by", "purpose", "attendees", "start", "end"]
