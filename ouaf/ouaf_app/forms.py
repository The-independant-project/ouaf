from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import PasswordInput
from .models import Person
from django import forms


class PersonForm(UserCreationForm):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Person
        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
            ]

        widgets = {
            "password1":PasswordInput(),
            "password2":PasswordInput(),
        }