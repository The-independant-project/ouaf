from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

ROLE_BACKOFFICE = "Backoffice"
ROLE_VOLUNTEER = "Volunteer"
ROLE_MEMBER = "Member"


def _perm(app_label, model, codename):
    app_model = ContentType.objects.get(app_label=app_label, model=model.lower())
    return Permission.objects.get(content_type=app_model, codename=codename)


@receiver(post_migrate)
def ensure_roles_and_permission(sender, **kwargs):
    backoffice, _ = Group.objects.get_or_create(name=ROLE_BACKOFFICE)
    volunteer, _ = Group.objects.get_or_create(name=ROLE_VOLUNTEER)
    member, _ = Group.objects.get_or_create(name=ROLE_MEMBER)

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

        person_view, person_change,

        animal_view, animal_add, animal_change, animal_delete,
        
        # memberpayment_view, memberpayment_add, memberpayment_change, memberpayment_delete,
    }

    volunteer.permissions.set({p for p in volunteer_perms if p})
    member.permissions.set({p for p in member_perms if p})
    backoffice.permissions.set({p for p in backoffice_perms if p})


def _ensure_group(name: str) -> Group:
    group, _ = Group.objects.get_or_create(name=name)
    return group


def _apply_member_flag(user):
    group = _ensure_group(ROLE_MEMBER)
    if user.is_member:
        user.groups.add(group)
    else:
        user.groups.remove(group)


def _apply_volunteer_flag(user):
    group = _ensure_group(ROLE_VOLUNTEER)
    if user.is_volunteer:
        user.groups.add(group)
    else:
        user.groups.remove(group)


@receiver(post_save, sender=User)
def sync_roles_after_user_save(sender, instance: User, **kwargs):
    _apply_member_flag(instance)
    _apply_volunteer_flag(instance)
