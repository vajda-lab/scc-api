from django.core.management.base import BaseCommand
from ftmap.models import Job
from django.utils import timezone
from datetime import datetime, timedelta
from constance import config

# docker-compose run django python manage.py remove_old_jobs


class Command(BaseCommand):
    help = "Delete objects older than 10 days"

    def handle(self, *args, **options):
        job_set = Job.objects.filter(
            last_modified__lt=datetime.now(tz=timezone.utc)
            - timedelta(days=config.DELETE_JOBS_AFTER)
        )
        for job in job_set:
            self.stdout.write("Deleting job {}".format(job.job_uuid))
            job.delete()
        self.stdout.write(
            "Deleted objects older than {} days".format(config.DELETE_JOBS_AFTER)
        )
