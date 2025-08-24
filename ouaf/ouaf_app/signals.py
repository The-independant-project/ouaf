from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .groups import *

User = get_user_model()


class PermissionDefiner:
    __app_name = ""
    __model_name = ""
    __codename = ""
    __model = None

    def __init__(self, app_name:str, model_name:str, codename:str):
        self.__app_name = app_name.lower()
        self.__model_name = model_name.lower()
        self.__codename = codename.lower()
        self.__model = None

    def _perm_object(self) -> Permission:
        if self.__model is None:
            self.__model = ContentType.objects.get(app_label=self.__app_name, model=self.__model_name)
        return Permission.objects.get(content_type=self.__model, codename=self.__codename)

    def perm_name(self) -> str:
        return f"{self.__app_name}.{self.__codename}"

def ensure_roles_and_permission(sender, **kwargs):
    backoffice, _ = Group.objects.get_or_create(name=GROUP_BACKOFFICE)
    volunteer, _ = Group.objects.get_or_create(name=GROUP_VOLUNTEER)
    member, _ = Group.objects.get_or_create(name=GROUP_MEMBER)

    #Here we define basic permissions

    #Here we assign permissions to roles
    volunteer_perms = {event_view}
    member_perms = {event_view}
    backoffice_perms = {
        event_view, event_add, event_change, event_delete, event_publish, can_change_user_role,
        service_view, service_add, service_change, service_delete,
        activite_view, activite_add, activite_change, activite_delete,
        person_view, person_change,
        animal_view, animal_add, animal_change, animal_delete,
        # memberpayment_view, memberpayment_add, memberpayment_change, memberpayment_delete,

        service_view, service_add, service_change, service_delete,
    }

    volunteer.permissions.set({p._perm_object() for p in volunteer_perms if p})
    member.permissions.set({p._perm_object() for p in member_perms if p})
    backoffice.permissions.set({p._perm_object() for p in backoffice_perms if p})


event_view = PermissionDefiner("ouaf_app", "event", "view_event")
event_add = PermissionDefiner("ouaf_app", "event", "add_event")
event_change = PermissionDefiner("ouaf_app", "event", "change_event")
event_delete = PermissionDefiner("ouaf_app", "event", "delete_event")
event_publish = PermissionDefiner("ouaf_app", "event", "can_publish_event")

person_view = PermissionDefiner("ouaf_app", "person", "view_person")
person_change = PermissionDefiner("ouaf_app", "person", "change_person")

animal_view = PermissionDefiner("ouaf_app", "animal", "view_animal")
animal_add = PermissionDefiner("ouaf_app", "animal", "add_animal")
animal_change = PermissionDefiner("ouaf_app", "animal", "change_animal")
animal_delete = PermissionDefiner("ouaf_app", "animal", "delete_animal")

service_view = PermissionDefiner("ouaf_app", "service", "view_service")
service_add = PermissionDefiner("ouaf_app", "service", "add_service")
service_change = PermissionDefiner("ouaf_app", "service", "change_service")
service_delete = PermissionDefiner("ouaf_app", "service", "delete_service")

activite_view = PermissionDefiner("ouaf_app", "activite", "view_activite")
activite_add = PermissionDefiner("ouaf_app", "activite", "add_activite")
activite_change = PermissionDefiner("ouaf_app", "activite", "change_activite")
activite_delete = PermissionDefiner("ouaf_app", "activite", "delete_activite")

can_change_user_role = PermissionDefiner("ouaf_app", "person", "can_change_user_role")

# memberpayment_view = _perm("ouaf_app", "memberpayment", "view_memberpayment")
# memberpayment_add = _perm("ouaf_app", "memberpayment", "add_memberpayment")
# memberpayment_change = _perm("ouaf_app", "memberpayment", "change_memberpayment")
# memberpayment_delete = _perm("ouaf_app", "memberpayment", "delete_memberpayment")