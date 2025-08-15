from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

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
    is_volunteer = models.BooleanField(default=False)
    is_member = models.BooleanField(default=False)
    newsletter_subscription = models.BooleanField(default=False)

class Event(models.Model):
    summary = models.CharField(max_length=500)
    description = models.CharField()
    start = models.DateTimeField()
    until = models.DateTimeField() # end date, primary cluster key of the table
    duration = models.DurationField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=None) # index
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL)
    address = models.CharField(max_length=1000)
    latitude = models.FloatField()
    longitude = models.FloatField()

class MemberPayment(models.Model):
    personId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=None) # index
    paymentDate = models.DateTimeField() # end date, primary cluster key of the table
    amount = models.FloatField()


class Animal(models.Model):
    name = models.CharField(max_length=100)
    birth = models.DateTimeField()
    death = models.DateTimeField()
    pet_amount = models.IntegerField()