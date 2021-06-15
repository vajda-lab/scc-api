from django.apps import AppConfig
from django.conf import settings


class UserAppConfig(AppConfig):
    name = "users"

    def ready(self):
        from . import signals  # noqa
