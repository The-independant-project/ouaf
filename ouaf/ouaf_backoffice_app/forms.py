from django import forms
from ouaf_app.models import Person, Animal
from ouaf_app.groups import *


class PersonEditForm(forms.ModelForm):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    is_volunteer = forms.BooleanField(required=False)
    is_member = forms.BooleanField(required=False)

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
            kwargs['initial'] = { 'is_volunteer': instance.belongs_to_group(GROUP_VOLUNTEER), 'is_member': instance.belongs_to_group(GROUP_MEMBER) }
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.set_group(GROUP_VOLUNTEER, self.cleaned_data['is_volunteer'])
        self.instance.set_group(GROUP_MEMBER,  self.cleaned_data['is_member'])
        return super().save(*args, **kwargs)


class AnimalMediaForm(forms.ModelForm):
    template_name = "backoffice/animals/baseForm.html"
    class Meta:
        model = Animal
        fields = ["name", "description", "birth", "death", "pet_amount"]