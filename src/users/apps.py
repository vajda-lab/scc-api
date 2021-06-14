from django.apps import AppConfig
from django.conf import settings
from .signals import create_auth_token

class UserAppConfig(AppConfig):
    name = "users"


    def ready(self):
        create_auth_token(sender=settings.AUTH_USER_MODEL)