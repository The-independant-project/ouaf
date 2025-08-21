from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import PasswordInput
from .models import Person
from django import forms


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
            kwargs['initial'] = { 'is_volunteer': instance.is_volunteer, 'is_member': instance.is_member, 'is_backoffice': instance.is_backoffice }
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.is_volunteer = self.cleaned_data['is_volunteer']
        self.instance.is_member = self.cleaned_data['is_member']
        self.instance.is_backoffice = self.cleaned_data['is_backoffice']
        return super().save(*args, **kwargs)