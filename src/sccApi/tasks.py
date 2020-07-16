from celery import task
from .models import Job

@task()
def create_job(job_uuid):
    job = Job(job_uuid=job_uuid)
    job.save()


