from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import PasswordInput
from .models import Person
from django import forms
import phonenumbers
from phonenumber_field.formfields import PhoneNumberField as PhoneFormField
from django.utils.translation import gettext_lazy as _


class RegistrationForm(UserCreationForm):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone_number = PhoneFormField(region="FR", required=True)

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
            "phone_number",
            "newsletter_subscription",
        ]
        widgets = {
            "password1": PasswordInput(),
            "password2": PasswordInput(),
        }


class PersonForm(forms.ModelForm):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone_number = PhoneFormField(region="FR", required=False)

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
            "phone_number",
            "newsletter_subscription",
        ]


class ContactForm(forms.Form):
    first_name = forms.CharField(
        label="Prénom",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Votre prénom"})
    )
    last_name = forms.CharField(
        label="Nom",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Votre nom"})
    )
    email = forms.EmailField(
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={"placeholder": "votre@email.com"})
    )
    phone = forms.CharField(
        label="Téléphone (facultatif)",
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "+33 6 12 34 56 78"})
    )
    message = forms.CharField(
        label="Votre message",
        widget=forms.Textarea(attrs={"placeholder": "Expliquez-nous votre demande…", "rows": 6})
    )

    def clean_phone(self):
        raw = self.cleaned_data.get("phone", "").strip()
        if not raw:
            return ""
        try:
            number = phonenumbers.parse(raw, "FR")
            if not phonenumbers.is_possible_number(number) or not phonenumbers.is_valid_number(number):
                raise forms.ValidationError("Le numéro de téléphone n'est pas valide.")
            return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise forms.ValidationError("Le numéro de téléphone n'est pas valide.")
