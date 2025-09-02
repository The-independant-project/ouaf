from django import forms
from ouaf_app.models import Person, Animal
from ouaf_app.groups import *
from django.utils.translation import gettext_lazy as _


class PersonEditForm(forms.ModelForm):
    username = forms.CharField(required=True, label=_("Nom d’utilisateur"))
    first_name = forms.CharField(required=True, label=_("Prénom"))
    last_name = forms.CharField(required=True, label=_("Nom"))
    email = forms.EmailField(required=True, label=_("Adresse e-mail"))
    is_volunteer = forms.BooleanField(required=False, label=_("Bénévole"))
    is_member = forms.BooleanField(required=False, label=_("Adhérent"))

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
        labels = {
            "address": _("Adresse"),
            "city": _("Ville"),
            "country": _("Pays"),
            "newsletter_subscription": _("Abonnement à la newsletter"),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs['initial'] = {
                'is_volunteer': instance.belongs_to_group(GROUP_VOLUNTEER),
                'is_member': instance.belongs_to_group(GROUP_MEMBER),
            }
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.set_group(GROUP_VOLUNTEER, self.cleaned_data['is_volunteer'])

        self.instance.set_group(GROUP_MEMBER, self.cleaned_data['is_member'])
        return super().save(*args, **kwargs)


class MediaForm(forms.ModelForm):
    template_name = "backoffice/forms/media.html"
