import logging

from .settings import *  # noqa

# Let's speed up our tests!

if "dashboard" in DATABASES:
    del DATABASES["dashboard"]

# Disable DEBUG
DEBUG = False

# Disable our logging
logging.disable(logging.CRITICAL)

# User a faster password hasher
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

CELERY_TASK_ALWAYS_EAGER = True

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
