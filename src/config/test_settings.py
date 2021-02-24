import logging

from .settings import *  # noqa

# Let's speed up our tests!

# Disable DEBUG
DEBUG = False

# Disable our logging
logging.disable(logging.CRITICAL)

# User a faster password hasher
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


# Disable migrations for all-the-things
class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

CELERY_TASK_ALWAYS_EAGER = True

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
