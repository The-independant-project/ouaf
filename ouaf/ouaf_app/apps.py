from django.apps import AppConfig


class OuafAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ouaf_app'

    def ready(self):
        from . import signals


