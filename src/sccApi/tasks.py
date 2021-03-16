from celery import task
from .models import Job


@task(bind=True)
def create_job_task(self, pk):
    print(f"create_job_task({pk})")
    job = Job.objects.get(pk=pk)
    job.status = Job.STATUS_ACTIVE
    job.save()
    # ToDo: use subprocess() to run qsub on the submit host

@task(bind=True)
def delete_job_task(self, pk):
    print(f"delete_job_task({pk})")    
    job = Job.objects.get(pk=pk)
    job.status = Job.STATUS_DELETE
    job.save()
    # ToDo: use subprocess() to run {delete job command} on the submit host

@task(bind=True)
def update_job_priority_task(self, pk):
    print(f"update_job_priority_task({pk})") 
    job = Job.objects.get(pk=pk)
    # ToDo: use subprocess() to run {command to change job priority} on the submit host
    # ToDo: later, add priority field to Job model & update job status to change priority

@task(bind=True)
def poll_job_task(self):
    print(f"poll_job_task()")
    # ToDo: use subprocess() to run qstat {get status of current jobs} on the submit host
    # ToDo: need to process qstat output to know what to do
