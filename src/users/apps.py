from django.apps import AppConfig
from django.conf import settings

class UserAppConfig(AppConfig):
    name = "users"


    def ready(self):
        from . import signals
        signals.create_auth_token(sender=settings.AUTH_USER_MODEL)