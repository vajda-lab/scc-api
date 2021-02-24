from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.views.generic.list import ListView

from rest_framework import viewsets

from .forms import SignUpForm

from .models import User
from . import serializers


class UserListView(ListView):
    """List view of current users."""

    model = User


def signup(request):
    """New user signup form."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


class UserViewSet(viewsets.ModelViewSet):
    """A viewset for viewing and editing User instances."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    ordering = "organization"
