from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.conf import settings
from .groups import *


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
    address = models.CharField(max_length=1000)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    newsletter_subscription = models.BooleanField(default=False)
    def belongs_to_group(self, group_name):
        return self.groups.filter(name=group_name).exists()
    def set_group(self, group_name, value):
        group = Group.objects.get(name=group_name)
        self.groups.add(group) if value else self.groups.remove(group)
    class Meta:
        permissions = [
            ("can_change_user_role", "Can change user roles")
        ]


class Event(models.Model):
    summary = models.CharField(max_length=500)
    description = models.TextField()
    start = models.DateTimeField()
    until = models.DateTimeField()  # end date, primary cluster key of the table
    duration = models.DurationField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                  related_name='organiser2person')  # index
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='attendees2person')
    address = models.CharField(max_length=1000)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_published = models.BooleanField(default=False)


    class Meta:
        permissions = [
            ("can_publish_event","Can publish an event"),
        ]

class MemberPayment(models.Model):
    personId = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)  # index
    paymentDate = models.DateTimeField()  # end date, primary cluster key of the table
    amount = models.FloatField()


class Animal(models.Model):
    name = models.CharField(max_length=100)
    birth = models.DateTimeField()
    death = models.DateTimeField()
    pet_amount = models.IntegerField()


class OrganisationChartEntry(models.Model):
    personId = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)  # index
    text = models.CharField(max_length=1000)
    photo = models.ImageField(upload_to='images/organisationChart', blank=True)

class Service(models.Model):
    title = models.CharField(max_length=1000)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to='images/services', blank=True)