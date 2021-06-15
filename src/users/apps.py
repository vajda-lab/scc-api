from django.apps import AppConfig
from django.conf import settings

class UserAppConfig(AppConfig):
    name = "users"


    def ready(self):
        from .signals import create_auth_token
        create_auth_token()