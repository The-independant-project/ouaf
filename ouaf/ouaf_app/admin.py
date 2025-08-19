from django.contrib import admin
from .models import *

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import Person, Event, MemberPayment, Animal, OrganisationChartEntry


@admin.register(Person)
class PersonAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "first_name", "last_name",
                    "is_active", "is_staff", "is_superuser",
                    "is_member", "is_volunteer")
    list_filter = ("is_active", "is_staff", "is_superuser", "is_member", "is_volunteer")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Informations personnelles", {
            "fields": ("first_name", "last_name", "email", "address", "city", "country",
                       "newsletter_subscription"),
        }),
        ("Rôles métier", {"fields": ("is_member", "is_volunteer")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2",
                       "first_name", "last_name", "email",
                       "address", "city", "country",
                       "newsletter_subscription",
                       "is_member", "is_volunteer",
                       "is_active", "is_staff", "is_superuser"),
        }),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("summary", "start", "until", "organizer", "is_published")
    list_filter = ("is_published", "start")
    search_fields = ("summary", "description")
    date_hierarchy = "start"
    autocomplete_fields = ("organizer", "attendees")  # pratique sur gros volumes


@admin.register(MemberPayment)
class MemberPaymentAdmin(admin.ModelAdmin):
    list_display = ("personId", "amount", "paymentDate")
    list_filter = ("paymentDate",)
    search_fields = ("personId__username", "personId__email")
    date_hierarchy = "paymentDate"
    autocomplete_fields = ("personId",)


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ("name", "birth", "death", "pet_amount")
    list_filter = ("birth", "death")
    search_fields = ("name",)
    date_hierarchy = "birth"


@admin.register(OrganisationChartEntry)
class OrganisationChartEntryAdmin(admin.ModelAdmin):
    list_display = ("personId", "text")
    search_fields = ("personId__username", "text")
    autocomplete_fields = ("personId",)