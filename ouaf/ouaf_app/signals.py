from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .groups import *

User = get_user_model()


def _perm(app_label, model, codename):
    app_model = ContentType.objects.get(app_label=app_label.lower(), model=model.lower())
    return Permission.objects.get(content_type=app_model, codename=codename)


@receiver(post_migrate)
def ensure_roles_and_permission(sender, **kwargs):
    backoffice, _ = Group.objects.get_or_create(name=GROUP_BACKOFFICE)
    volunteer, _ = Group.objects.get_or_create(name=GROUP_VOLUNTEER)
    member, _ = Group.objects.get_or_create(name=GROUP_MEMBER)

    #Here we define basic permissions
    event_view = _perm("ouaf_app", "event", "view_event")
    event_add = _perm("ouaf_app", "event", "add_event")
    event_change = _perm("ouaf_app", "event", "change_event")
    event_delete = _perm("ouaf_app", "event", "delete_event")

    person_view = _perm("ouaf_app", "person", "view_person")
    person_change = _perm("ouaf_app", "person", "change_person")

    animal_view = _perm("ouaf_app", "animal", "view_animal")
    animal_add = _perm("ouaf_app", "animal", "add_animal")
    animal_change = _perm("ouaf_app", "animal", "change_animal")
    animal_delete = _perm("ouaf_app", "animal", "delete_animal")

    service_view = _perm("ouaf_app", "service", "view_service")
    service_add = _perm("ouaf_app", "service", "add_service")
    service_change = _perm("ouaf_app", "service", "change_service")
    service_delete = _perm("ouaf_app", "service", "delete_service")
    
    activite_view = _perm("ouaf_app", "activite", "view_activite")
    activite_add = _perm("ouaf_app", "activite", "add_activite")
    activite_change = _perm("ouaf_app", "activite", "change_activite")
    activite_delete = _perm("ouaf_app", "activite", "delete_activite")

    # memberpayment_view = _perm("ouaf_app", "memberpayment", "view_memberpayment")
    # memberpayment_add = _perm("ouaf_app", "memberpayment", "add_memberpayment")
    # memberpayment_change = _perm("ouaf_app", "memberpayment", "change_memberpayment")
    # memberpayment_delete = _perm("ouaf_app", "memberpayment", "delete_memberpayment")

    #Here we define custom permission based on models meta classes.
    try:
        event_publish = _perm("ouaf_app", "event", "can_publish_event")
    except Permission.DoesNotExist:
        event_publish = None

    try:
        user_role = _perm("ouaf_app", "person", "can_change_user_role")
    except Permission.DoesNotExist:
        user_role = None

    #Here we assign permissions to roles
    volunteer_perms = {event_view}
    member_perms = {event_view}
    backoffice_perms = {
        event_view, event_add, event_change, event_delete, event_publish, user_role,
        service_view, service_add, service_change, service_delete,
        activite_view, activite_add, activite_change, activite_delete,
        person_view, person_change,
        animal_view, animal_add, animal_change, animal_delete,
        # memberpayment_view, memberpayment_add, memberpayment_change, memberpayment_delete,
    }

    volunteer.permissions.set({p for p in volunteer_perms if p})
    member.permissions.set({p for p in member_perms if p})
    backoffice.permissions.set({p for p in backoffice_perms if p})