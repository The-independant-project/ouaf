from django.apps import AppConfig
from django.db.models.signals import post_migrate



class OuafAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ouaf_app'

    def ready(self):
        from .signals import ensure_roles_and_permission
        post_migrate.connect(ensure_roles_and_permission, sender=self, dispatch_uid="ouaf_app_post_migrate")
        # from . import signals


