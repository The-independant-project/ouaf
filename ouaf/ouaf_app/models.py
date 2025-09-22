from mimetypes import guess_type

from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.conf import settings
from .groups import *
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.

class Person(AbstractUser):
    """
    https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.AbstractBaseUser
    id
    password
    username (Special, Unique Constraint)
    first_name
    last_name
    email (Special)
    last_login
    is_staff : Returns True if the user is allowed to have access to the admin site.
    is_superuser : Designates that this user has all permissions without explicitly assigning them.
    is_active
    date_joined
    """
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("Un utilisateur avec cet email existe déjà."),
        },
    )
    address = models.CharField(_("Adresse"), max_length=1000)
    city = models.CharField(_("Ville"), max_length=100)
    country = models.CharField(_("Pays"), max_length=100)
    newsletter_subscription = models.BooleanField(_("Abonnement à la newsletter"), default=False)
    phone_number = PhoneNumberField(
        _("Téléphone"),
        region="FR",
        null=True,
        blank=False
    )

    def belongs_to_group(self, group_name):
        return self.groups.filter(name=group_name).exists()

    def set_group(self, group_name, value):
        group = Group.objects.get(name=group_name)
        self.groups.add(group) if value else self.groups.remove(group)

    class Meta:
        permissions = [
            ("can_change_user_role", _("Peut changer les rôles utilisateurs"))
        ]


class Event(models.Model):
    summary = models.CharField(_("Résumé"), max_length=500)
    description = models.TextField(_("Description"))
    start = models.DateTimeField(_("Date de début"))
    until = models.DateTimeField(_("Date de fin"))
    duration = models.DurationField(_("Durée"))
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Organisateur"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="organiser2person"
    )
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Participants"),
        related_name="attendees2person"
    )
    address = models.CharField(_("Adresse"), max_length=1000)
    latitude = models.FloatField(_("Latitude"))
    longitude = models.FloatField(_("Longitude"))
    is_published = models.BooleanField(_("Publié"), default=False)

    class Meta:
        permissions = [
            ("can_publish_event", _("Peut publier un événement")),
        ]


class MemberPayment(models.Model):
    personId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Personne"),
        null=True,
        on_delete=models.SET_NULL
    )
    paymentDate = models.DateTimeField(_("Date de paiement"))
    amount = models.FloatField(_("Montant"))


class Animal(models.Model):
    name = models.CharField(_("Nom"), max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    birth = models.DateField(_("Date de naissance"), null=True, blank=True)
    death = models.DateField(_("Date de décès"), null=True, blank=True)
    pet_amount = models.PositiveIntegerField(_("Nombre de caresses"), default=0, blank=True)


class OrganisationChartEntry(models.Model):
    first_name = models.CharField(_("Prénom"), max_length=1000)
    last_name = models.CharField(_("Nom"), max_length=1000)
    role = models.CharField(_("Rôle"), max_length=128)
    description = models.TextField(_("Description"), max_length=1000)
    photo = models.ImageField(_("Photo"), upload_to='images/organisationChart', blank=True)


class ActivityCategory(models.Model):
    title = models.CharField(_("Titre"), max_length=100)
    image = models.ImageField(_("Image"), upload_to='images/categories')

    def __str__(self):
        return self.title


class Activity(models.Model):
    title = models.CharField(_("Titre"), max_length=1000)
    category = models.ForeignKey(ActivityCategory, verbose_name=_("Catégorie"), null=True, blank=True,
                                 on_delete=models.CASCADE)
    description = models.TextField(_("Description"))


class AbstractMedia(models.Model):
    url = models.URLField(_("URL"), blank=True)
    caption = models.CharField(_("Légende"), max_length=200, blank=True)
    position = models.PositiveIntegerField(_("Position"), default=0)

    class Meta:
        abstract = True
        ordering = ["position", "id"]

    def __str__(self):
        return self.caption or (self.file.name if self.file else self.url or "media")

    @property
    def mime(self):
        src = self.file.name if self.file else self.url
        m, _ = guess_type(src or "")
        return m or ""

    @property
    def is_image(self):
        return self.mime.startswith("image/")

    @property
    def is_video(self):
        return self.mime.startswith("video") or ("youtu" in (self.url or ""))


class ActivityMedia(AbstractMedia):
    activity = models.ForeignKey(Activity, verbose_name=_("Activité"), on_delete=models.CASCADE, related_name="media")
    file = models.FileField(_("Fichier"), upload_to='activities/media', blank=True)

    class Meta:
        ordering = ["position", "id"]

class AnimalMedia(AbstractMedia):
    animal = models.ForeignKey(Animal, null=False, blank=False, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to="animals/media", null=False, blank=False)
    def __str__(self):
        return f"{self.animal.name} - {super().__str__()}"
    class Meta:
        ordering = ["position", "id"]
