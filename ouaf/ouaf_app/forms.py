from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import PasswordInput
from .models import Person
from django import forms
from .groups import *


class RegistrationForm(UserCreationForm):
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
            "address",
            "city",
            "country",
            "newsletter_subscription",
            ]
        widgets = {
            "password1":PasswordInput(),
            "password2":PasswordInput(),
        }

class PersonForm(forms.ModelForm):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    is_volunteer = forms.BooleanField(required=False)
    is_member = forms.BooleanField(required=False)
    is_backoffice = forms.BooleanField(required=False)

    class Meta:
        model = Person
        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
            "address",
            "city",
            "country",
            "newsletter_subscription",
            ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs['initial'] = { 'is_volunteer': instance.belongs_to_group(GROUP_VOLUNTEER), 'is_member': instance.belongs_to_group(GROUP_MEMBER), 'is_backoffice': instance.belongs_to_group(GROUP_BACKOFFICE) }
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.set_group(GROUP_VOLUNTEER, self.cleaned_data['is_volunteer'])
        self.instance.set_group(GROUP_MEMBER,  self.cleaned_data['is_member'])
        self.instance.set_group(GROUP_BACKOFFICE,  self.cleaned_data['is_backoffice'])
        return super().save(*args, **kwargs)