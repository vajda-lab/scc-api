from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    short_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    email = forms.EmailField(
        max_length=254, help_text="Required. Inform a valid email address."
    )

    class Meta:
        model = User
        fields = (
            "full_name",
            "short_name",
            "affiliation",
            "organization",
            "email",
            "password1",
            "password2",
        )
