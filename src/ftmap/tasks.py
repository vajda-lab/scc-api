from celery import task
from .models import Job

@task()
def create_job(job_name):
    job = Job(job_name=job_name)
    job.save()


