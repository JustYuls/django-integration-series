from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render

from .forms import SignUpForm
from .roles import STUDENT


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()  # the password is hashed by Django, never stored as typed
        user.groups.add(Group.objects.get(name=STUDENT))  # everyone who signs up is a Student
        login(request, user)
        messages.success(request, "Welcome! Your account is ready.")
        return redirect("home")
    return render(request, "accounts/signup.html", {"form": form})
