from celery import task
from .models import Job

# Group of Celery task actions
@task(bind=True)
def create_job(self, pk):
    job = Job.objects.get(pk=pk)
    job.status = Job.STATUS_ACTIVE
    job.save()
    # ToDo: use subprocess() to run qsub on the submit host


@task(bind=True)
def delete_job(self, pk):
    job = Job.objects.get(pk=pk)
    job.status = Job.STATUS_DELETED
    job.save()
    # ToDo: use subprocess() to run {delete job command} on the submit host


@task(bind=True)
def update_job_priority(self, pk, new_priority):
    job = Job.objects.get(pk=pk)
    # Current assumption, only 2 queues: standard & priority
    # If more priority levels are added, logic will need to change
    job.priority = new_priority
    job.save()
    # ToDo: use subprocess() to run {command to change job priority} on the submit host
    # ToDo: https://github.com/tveastman/secateur/blob/master/secateur/settings.py#L241-L245
        # Do we need to explicitly create separate queues in settings?
    # ToDo: We'll need to pass job.priority into this task, if we add a priority field to Job (this comment doesn't make sense); Comment makes sense if more than 2 priority levels


@task(bind=True)
def poll_job(self):
    print(f"poll_job()")
    return True
    # ToDo: use subprocess() to run qstat {get status of current jobs} on the submit host
    # ToDo: need to process qstat output to know what to do
    # ToDo: Read about mocking (Thea's article)
    # ToDo: Set up a schedule to run the poll job at regular intervals
    # ToDo: search for "assert_called_once_with" section in Thea's article
    # ToDo: Scheduling model code https://github.com/revsys/git-shoes/blob/main/config/settings.py#L249-L251
