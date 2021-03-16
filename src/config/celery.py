import os
from celery import Celery
from celery.schedules import crontab

# from celery.decorators import periodic_task

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("sccApi")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


# @periodic_task(run_every=(crontab(minute='*/1')), name="some_task", ignore_result=True)
# ToDo: We'll need to run something like the line above; prob turn on in config.settings
def some_task():
    print("puthons are magic")

# NOTES: refer to https://github.com/tveastman/secateur/blob/master/secateur/tasks.py#L118
# And the Repo in general