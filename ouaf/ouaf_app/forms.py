from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import PasswordInput
from .models import Person
from django import forms
import phonenumbers
from phonenumber_field.formfields import PhoneNumberField as PhoneFormField
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import time


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
    """
    Contact form with anti-spam protection.

    This form collects basic contact information (first name, last name,
    email, phone, and message) while implementing simple anti-spam
    mechanisms:
      - **Honeypot field**: A hidden field that should remain empty.
        If filled, the submission is flagged as spam.
      - **Timestamp field**: Ensures the form is not submitted too quickly
        (less than 3 seconds, typical of bots) and prevents submissions of
        expired forms (older than 1 hour).
      - **Phone number validation**: Uses the `phonenumbers` library to
        validate and normalize the phone number into E.164 format.

    Fields:
        honeypot (CharField): Hidden anti-spam field, must remain empty.
        ts (IntegerField): Timestamp set on form render, used to detect
            rapid or expired submissions.
        first_name (CharField): User's first name.
        last_name (CharField): User's last name.
        email (EmailField): User's email address.
        phone (CharField): User's phone number, validated and normalized.
        message (CharField): The content of the user's message.

    Validation:
        - `clean_honeypot()`: Raises a ValidationError if the field is filled.
        - `clean_ts()`: Ensures the form is not submitted too quickly
          and has not expired.
        - `clean_phone()`: Validates and formats the phone number
          using the `phonenumbers` library.
    """
    honeypot = forms.CharField(
        required=False,
        label="Laissez ce champ vide",
        widget=forms.TextInput(attrs={
            "autocomplete": "off",
            "tabindex": "-1",
            "aria-hidden": "true",
            "style": "position:absolute;left:-9999px;top:-9999px;height:0;width:0;padding:0;border:0;"
        })
    )
    ts = forms.IntegerField(widget=forms.HiddenInput)

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
        label="Téléphone",
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "+33 6 12 34 56 78"})
    )
    message = forms.CharField(
        label="Votre message",
        widget=forms.Textarea(attrs={"placeholder": "Expliquez-nous votre demande…", "rows": 6})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields["ts"].initial = int(time.time())

    def clean_honeypot(self):
        if self.cleaned_data.get("honeypot"):
            raise ValidationError("Spam détecté.")
        return ""

    def clean_ts(self):
        """Empêche la soumission ‘instantanée’ (bots) et les liens périmés."""
        now = int(time.time())
        ts = int(self.cleaned_data.get("ts") or 0)
        if now - ts < 3:
            raise ValidationError("Soumission trop rapide, veuillez réessayer.")
        if now - ts > 3600:
            raise ValidationError("Le formulaire a expiré, veuillez le recharger.")
        return ts

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
