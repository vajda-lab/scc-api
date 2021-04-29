import logging
import pytz
import subprocess
import tarfile
import tempfile

from celery import task
from dateutil.parser import parse
from django.conf import settings
from pathlib import Path

from .models import Job, JobLog, Status

# from sccApi.mangement.commands.parse_qstat_demo import parse_output

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Group of Celery task actions
@task(bind=True)
def activate_job(self, *, pk, **kwargs):
    """
    Takes existing Job object instances from Django API
    Submits their data to the SCC for processing

    called via: `scheduled_allocate_job`

    """
    try:
        job = Job.objects.get(pk=pk)

        if job.status == Status.QUEUED:
            job.status = Status.ACTIVE

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
                    job_submit = subprocess.run(cmd, capture_output=True, text=True)
                else:
                    job_submit = subprocess.run([cmd], capture_output=True, text=True)

                # Assign SGE ID to job
                # Successful qsub stdout = Your job 6274206 ("ls -al") has been submitted
                sge_task_id = job_submit.stdout.split(" ")[2]
                job.sge_task_id = int(sge_task_id)
                JobLog.objects.create(job=job, event="Job sge_task_id added")
                return job_submit
            except Exception as e:
                job.status = Status.ERROR
                logger.exception()
            finally:
                job.save()
        else:
            return None

    except Job.DoesNotExist:
        logger.exception(f"Job {pk} does not exist")


@task(bind=True)
def delete_job(self, *, pk, **kwargs):
    """
    Sets Job.status to Status.DELETED in Django
    Also delete job directory and associated files on SCC
    """
    try:
        job = Job.objects.get(pk=pk)

        if job.status != Status.DELETED:
            job.status = Status.DELETED
            job.save()
            JobLog.objects.create(job=job, event="Job status changed to deleted")

        # Grid Engine Qdel ONLY stops/deletes a job. We have to handle file system.
        cmd = settings.GRID_ENGINE_DELETE_CMD.split(" ")
        if isinstance(cmd, list):
            job_delete = subprocess.run(cmd, capture_output=True)
        else:
            job_delete = subprocess.run([cmd], capture_output=True)

        # Remove temp dir created in activate_job
        scc_job_dir = str(job.uuid)
        if Path(f"/tmp/{scc_job_dir}").exists():
            subprocess.run(["rm", "-rf", f"/tmp/{scc_job_dir}"])

        # This return was for testing early mocked command
        return job_delete

    except Job.DoesNotExist:
        logger.exception(f"Job {pk} does not exist")


def parse_output(output):
    lines = [line for line in output.split("\n") if len(line)]
    header_keys = [column for column in lines[0].split(" ") if len(column)]
    print(header_keys)

    headers = {}
    header_cols = []
    for header_col in range(len(header_keys)):
        header = header_keys[header_col]
        start = lines[0].find(header)
        try:
            next_header = header_keys[header_col + 1]
            end = lines[0].find(next_header)
        except IndexError:
            end = None

        header_cols.append(start)
        headers[header] = {
            "name": header,
            "start": start,
            "end": end,
        }

    rows = []
    for row in lines[2:]:
        data = {}
        for column in headers:
            start = headers[column]["start"]
            end = headers[column]["end"]
            if end:
                data[column] = row[start:end]
            else:
                data[column] = row[start:]
        rows.append(data)
    return rows


@task(bind=True)
def scheduled_allocate_job(self):
    """
    Allocates existing Job instances to Celery at a set interval
    Interval determined by settings.CELERY_BEAT_SCHEDULE
    Should do so based on availability of different priority queues
    """
    # Look at how many jobs are Status.QUEUED, and Status.ACTIVE
    queued_jobs = Job.objects.filter(status=Status.QUEUED).count()
    active_jobs = Job.objects.filter(status=Status.ACTIVE).count()

    # ToDo: add settings for MaxValues of Low, Normal, & High priority jobs
    # settings.MAX_HIGH_JOBS
    queued_jobs = Job.objects.filter(status=Status.QUEUED)
    for queued_job in queued_jobs:
        activate_job.delay(pk=queued_job.pk)

    # For each priorty, give count of Status.ACTIVE jobs
    # Based on limits per priority queue, decide which Celery queue to send new jobs to


@task(bind=True)
def scheduled_capture_job_output(self):
    """
    Periodically captures output files from Status.COMPLETE & Status.ERROR jobs to the web app
    Will also delete those directories from SCC
    Interval determined by settings.CELERY_BEAT_SCHEDULE
    UNFINISHED!
    """
    complete_jobs = Job.objects.filter(status=Status.COMPLETE)

    for job in complete_jobs:
        # Find and TAR output files
        # Assign TAR file to job.output_file
        job.save()


@task(bind=True)
def scheduled_poll_job(self):
    """
    Checks status of current SCC jobs at a set interval
    Interval determined by settings.CELERY_BEAT_SCHEDULE

    This task will also find finished jobs:
    1. Check that the job is NOT in the queue (so, we shouldn’t see that job_id in qstat results)
    2. Look for the Output and/or Error files in the job’s target directory
    3. Do Both

    """
    cmd = settings.GRID_ENGINE_STATUS_CMD.split(" ")
    if isinstance(cmd, list):
        job_poll = subprocess.run(cmd, capture_output=True, text=True)
    else:
        job_poll = subprocess.run([cmd], capture_output=True, text=True)

    # Capture qstat info as a list of dictionaries
    qstat_output = parse_output(job_poll)
    # Update jobs w/ qstat info
    update_jobs(qstat_output)

    # Create django_scc_map (list of {uuid: sge_task_id} dicts)

    active_jobs = Job.objects.filter(status=Status.ACTIVE)
    # Broken pseudocode below
    for job in active_jobs:
        if job.sge_task_id not in django_scc_map:
            # Find and TAR output files
            # Assign TAR file to job.output_file
            job.save()

    # kombu.exceptions.EncodeError: Object of type CompletedProcess is not JSON serializable
    # Returning portions of CompletedProcess to avoid error
    # kombu.exceptions.EncodeError: Object of type bytes is not JSON serializable
    # return (job_poll.args, job_poll.returncode, job_poll.stdout)
    # ToDo: use subprocess() to run qstat {get status of current jobs} on the submit host
    # ToDo: search for "assert_called_once_with" section in Thea's article
    # ToDo: Scheduling model code https://github.com/revsys/git-shoes/blob/main/config/settings.py#L249-L251


def update_jobs(qstat_output):
    """
    Takes input from scheduled_poll_job (a list of dictionaries)
    Parses that and saves the results to job objects in the web app
    Also updates Job.Status on jobs that have Errored or are complete
    """
    # Update all jobs w/ their qstat results
    for row in qstat_output:
        try:
            job_id = row["job-ID"]
            job_ja_task_id = row.get("ja-task-ID")
            job_state = row["state"]
            job_submitted = f"{row['submit-start-at']}".replace("/", "-")
            job_submitted = parse(job_submitted)

            if job_submitted:
                job_submitted = pytz.timezone(settings.TIME_ZONE).localize(
                    job_submitted, is_dst=None
                )

            job, created = Job.objects.update_or_create(
                sge_task_id=job_id,
                defaults={
                    "job_data": row,
                    "job_ja_task_id": job_ja_task_id,
                    "job_state": job_state,
                    "job_submitted": job_submitted,
                    # "user": user,
                },
            )
            JobLog.objects.create(job=job, event="Job updated with qstat info")
        except Exception as e:
            print(f"{job_id} :: {e}")

    # Update status for Error jobs
    error_jobs = Job.objects.filter(job_state="Eqw")
    for job in error_jobs:
        job.status = Status.ERROR
        JobLog.objects.create(job=job, event="Job status changed to error")
    Job.objects.bulk_update(error_jobs, ["status"])

    # Update status for Complete jobs


@task(bind=True)
def update_job_priority(self, *, pk, new_priority, **kwargs):
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
        logger.exception(f"Job {pk} does not exist")
