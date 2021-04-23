import subprocess
import tarfile
import tempfile

from celery import task
from django.conf import settings
from pathlib import Path

from .models import Job, JobLog

# Group of Celery task actions
@task(bind=True)
def activate_job(self, pk):
    """
    Takes existing Job object instances from Django API
    Submits their data to the SCC for processing

    called via: `scheduled_allocate_job`

    """
    try:
        job = Job.objects.get(pk=pk)
        if job.status == Job.STATUS_QUEUED:
            job.status = Job.STATUS_ACTIVE

            # ToDO: Figure out how to make sure directory setup runs on SCC
            # Setup SCC job directory; this may change based on container situation
            scc_job_dir = str(job.uuid)
            scc_input_file = str(
                job.input_file
            )  # Will this work? Or does the file need to be opened/read?

            # Roll a temp folder variable instead
            if not Path(f"/tmp/{scc_job_dir}").exists():
                subprocess.run(["mkdir", f"/tmp/{scc_job_dir}"])

            if not Path(f"/tmp/{scc_job_dir}/{scc_input_file}").exists():
                subprocess.run(
                    ["tar", "-xf", f"{scc_input_file}", "-C", f"/tmp/{scc_job_dir}"]
                )

            JobLog.objects.create(job=job, event="Job status changed to active")

            # ToDo: use subprocess() to run qsub on the submit host
            # ToDo: how to "point" qsub at the right directory?
            try:
                cmd = settings.GRID_ENGINE_SUBMIT_CMD.split(" ")
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

    except Job.DoesNotExist:
        print(f"Job {pk} does not exist")


@task(bind=True)
def delete_job(self, pk):
    """
    Sets Job.status to STATUS_DELETED in Django
    Also delete job directory and associated files on SCC
    """
    try:
        job = Job.objects.get(pk=pk)

        if job.status != Job.STATUS_DELETED:
            job.status = Job.STATUS_DELETED
            job.save()
            JobLog.objects.create(job=job, event="Job status changed to deleted")

        # ToDo: use subprocess() to run {delete job command} on the submit host
        cmd = settings.GRID_ENGINE_DELETE_CMD.split(" ")
        if isinstance(cmd, list):
            job_delete = subprocess.run(cmd, capture_output=True)
        else:
            job_delete = subprocess.run([cmd], capture_output=True)

        return job_delete

    except Job.DoesNotExist:
        print(f"Job {pk} does not exist")


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
        activate_job.delay(pk=queued_job.pk)
    # For each priorty, give count of STATUS_ACTIVE jobs
    # Based on limits per priority queue, decide which Celery queue to send new jobs to


@task(bind=True)
def scheduled_poll_job(self):
    """
    Checks status of current SCC jobs at a set interval
    Interval determined by settings.CELERY_BEAT_SCHEDULE
    """
    cmd = settings.GRID_ENGINE_STATUS_CMD.split(" ")
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
def update_job_priority(self, pk, new_priority):
    """
    Update Job.priority
    Update priority on SCC or via Celery (unknown)
    """
    try:
        job = Job.objects.get(pk=pk)
        # Current assumption, only 2 queues: standard & priority
        # If more priority levels are added, logic will need to change
        job.priority = new_priority
        job.save()

        JobLog.objects.create(job=job, event=f"Job priority changed to {new_priority}")

        # ToDo: use subprocess() to run {command to change job priority} on the submit host
        # ToDo: https://github.com/tveastman/secateur/blob/master/secateur/settings.py#L241-L245
        # ToDo: Decide how we're handline priority, mechanically
        # Do we need to explicitly create separate queues in settings? Or change priority on SCC?

    except Job.DoesNotExist:
        print(f"Job {pk} does not exist")
