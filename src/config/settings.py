"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os
from environ import Env, Path

from celery.schedules import crontab

env = Env()

BASE_DIR = Path(__file__) - 3

SECRET_KEY = env.str("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "constance",
    "django_extensions",
    # "django_sql_dashboard",
    "django_filters",
    "rest_framework",
    "rest_framework.authtoken",
    # our apps
    "jobs",
    "users",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "constance.context_processors.config",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    "default": env.db("DATABASE_URL"),
}
# dashboard database for `django-sql-dashboard`
DATABASES["dashboard"] = DATABASES["default"].copy()
DATABASES["dashboard"]["OPTIONS"] = {
    "options": "-c default_transaction_read_only=on -c statement_timeout=100"
}
DATABASES["dashboard"]["TEST"] = {"LEGACY": True}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

CONSTANCE_REDIS_CONNECTION = "redis://redis:6379/0"


CONSTANCE_ADDITIONAL_FIELDS = {
    "yes_no_select": [
        "django.forms.fields.ChoiceField",
        {"widget": "django.forms.Select", "choices": (("yes", "Yes"), ("no", "No"))},
    ],
}

CONSTANCE_CONFIG = {
    "ACCEPTING_JOBS": ("yes", "select yes or no", "yes_no_select"),
    "BANNER_ON": ("no", "select yes or no", "yes_no_select"),
    "BANNER_MESSAGE": (
        "Our server is down for maintenance. We are not accepting new jobs at this time.",
        "Enter a message to be displayed on the site-wide banner.",
    ),
    "DELETE_JOBS_AFTER": (
        30,
        "Delete jobs that have not been modified in X days.",
        int,
    ),
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_USER_MODEL = "users.User"
AUTH_PREFIX = "django.contrib.auth.password_validation."
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": AUTH_PREFIX + "UserAttributeSimilarityValidator",
        "OPTIONS": {"user_attributes": ("email", "full_name", "short_name")},
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), "assets"]

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

LOGIN_REDIRECT_URL = "/"


# Celery
# ------------------------------------------------------------------------------
if USE_TZ:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json"]
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERYD_TASK_TIME_LIMIT = 15 * 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-soft-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERYD_TASK_SOFT_TIME_LIMIT = 60
CELERY_BEAT_SCHEDULE = {
    "poll-job": {
        "schedule": crontab(minute="*/1"),  # every minute
        "task": "jobs.tasks.scheduled_poll_job",
    },
    "allocate-job": {
        "schedule": crontab(minute="*/1"),  # every minute
        "task": "jobs.tasks.scheduled_allocate_job",
    },
}

# DRF Settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.CursorPagination",
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "PAGE_SIZE": 100,
}

# Grid Engine Commands
GRID_ENGINE_DELETE_CMD = env("GRID_ENGINE_DELETE_CMD", default="/app/bin/qdel")
GRID_ENGINE_STATUS_CMD = env("GRID_ENGINE_STATUS_CMD", default="/app/bin/qstat")
GRID_ENGINE_SUBMIT_CMD = env("GRID_ENGINE_SUBMIT_CMD", default="/app/bin/qsub")

# SCC Settings...
SCC_DEFAULT_EMAIL = env("SCC_DEFAULT_EMAIL", default="awake@bu.edu")
SCC_FTPLUS_PATH = env("SCC_FTPLUS_PATH", default="/tmp/")
SCC_API_TOKEN = env("SCC_API_TOKEN", default="")
SCC_API_URL = env("SCC_API_URL", default="http://ftplus.bu.edu:8000/apis")

# TASK QUEUE SETTINGS
SCC_MAX_HIGH_JOBS = env.int("SCC_MAX_HIGH_JOBS", default=50)
SCC_MAX_LOW_JOBS = env.int("SCC_MAX_LOW_JOBS", default=25)
SCC_MAX_NORMAL_JOBS = env.int("SCC_MAX_NORMAL_JOBS", default=25)
