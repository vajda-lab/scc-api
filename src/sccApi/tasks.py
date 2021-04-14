import subprocess
from celery import task
from .models import Job
from django.conf import settings

# Group of Celery task actions
@task(bind=True)
def create_job(self, pk):
    """
    Takes existing Job object instances
    Submits their data to the SCC.
    """
    job = Job.objects.get(pk=pk)
    if job.status == Job.STATUS_QUEUED:
        job.status = Job.STATUS_ACTIVE
        # ToDo: use subprocess() to run qsub on the submit host
        try:
            cmd = settings.GE_SUBMIT.split(" ")
            if isinstance(cmd, list):
                job_submit = subprocess.run(cmd, capture_output=True)
            else:
                job_submit = subprocess.run([cmd], capture_output=True)        
            return job_submit
        except Exception as e:
            job.status = Job.STATUS_ERROR
        finally:
            job.save()
    else:
        return None


@task(bind=True)
def delete_job(self, pk):
    job = Job.objects.get(pk=pk)
    job.status = Job.STATUS_DELETED
    job.save()
    # ToDo: use subprocess() to run {delete job command} on the submit host
    cmd = settings.GE_DELETE.split(" ")
    if isinstance(cmd, list):
        job_delete = subprocess.run(cmd, capture_output=True)
    else:
        job_delete = subprocess.run([cmd], capture_output=True)        
    return job_delete


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
def scheduled_poll_job(self):
    """
    Checks status of current SCC jobs at a set interval
    Interval determined by settings.CELERY_BEAT_SCHEDULE
    """
    cmd = settings.GE_STATUS.split(" ")
    if isinstance(cmd, list):
        job_poll = subprocess.run(cmd, capture_output=True)
    else: 
        job_poll = subprocess.run([cmd], capture_output=True)

    # Ask Amanda if the want output from this captured in the model?
    # Do we want an automated running w/ Job ID or USER ID?
        # If so, do you want it captured in the model?

    # Capturing QSTAT info
        # Parsing QSTAT output to save to model

    # kombu.exceptions.EncodeError: Object of type CompletedProcess is not JSON serializable
    # Returning portions of CompletedProcess to avoid error
    # kombu.exceptions.EncodeError: Object of type bytes is not JSON serializable
    # return (job_poll.args, job_poll.returncode, job_poll.stdout)
    # ToDo: use subprocess() to run qstat {get status of current jobs} on the submit host
    # ToDo: need to process qstat output to know what to do
    # ToDo: Read about mocking (Thea's article)
    # ToDo: search for "assert_called_once_with" section in Thea's article
    # ToDo: Scheduling model code https://github.com/revsys/git-shoes/blob/main/config/settings.py#L249-L251


@task(bind=True)
def scheduled_allocate_job(self):
    """
    Allocates existing Job instances to Celery at a set interval
    Interval determined by settings.CELERY_BEAT_SCHEDULE
    Should do so based on availability of different priority queues
    """
    # Look at how many jobs are STATUS_QUEUED, and STATUS_ACTIVE
    queued_jobs = Job.objects.filter(status=Job.STATUS_QUEUED).count()
    active_jobs = Job.objects.filter(status=Job.STATUS_ACTIVE).count()

    # ToDo: add settings for MaxValues of Low, Normal, & High priority jobs
    # settings.MAX_HIGH_JOBS
    queued_jobs = Job.objects.filter(status=Job.STATUS_QUEUED)
    for queued_job in queued_jobs:
        # queued_job.status = Job.STATUS_ACTIVE
        # queued_job.save()
        create_job.delay(pk=queued_job.pk)
    # For each priorty, give count of STATUS_ACTIVE jobs
    # Based on limits per priority queue, decide which Celery queue to send new jobs to




