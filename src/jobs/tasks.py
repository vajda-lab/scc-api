import celery
import logging
import pytz
import requests
import subprocess
import typing
import uuid

from celery import task
from datetime import datetime as dt
from datetime import timedelta
from dateutil.parser import parse
from django.conf import settings
from django.db.models import F
from django.utils import timezone
from pathlib import Path

from jobs.models import Job, JobLog, Priority, Status
from jobs.serializers import JobSerializer
from jobs.utils import TokenAuth
from users.models import User


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

##test for push
# Group of Celery task actions
@task(bind=True, ignore_result=True)
def activate_job(self: celery.Task, *, pk: typing.Union[str, uuid.UUID]):
    """
    Takes existing Job object instances from Django API
    Submits their data to the SCC for processing

    called via: `scheduled_allocate_job`

    """
    try:
        job = Job.objects.get(pk=pk)

        if job.status == Status.QUEUED:
            job.status = Status.ACTIVE

            ftplus_path = Path(
                settings.SCC_FTPLUS_PATH, "jobs-in-process", f"{job.uuid}"
            )

            # have we already untarred our job files?
            if not ftplus_path.exists():
                ftplus_path.mkdir(parents=True)
                subprocess.run(
                    [
                        "tar",
                        "-xf",
                        f"{job.input_file.path}",
                        "-C",
                        f"{ftplus_path}",
                    ]
                )

            # Ensure {ftplus_path}/settings.SCC_RUN_FILE exists
            try:
                runfile = ftplus_path.joinpath(settings.SCC_RUN_FILE)
                if not runfile.exists():
                    raise Exception(f"{settings.SCC_RUN_FILE} doesn't exist")

                JobLog.objects.create(job=job, event="Job status changed to active")

                if job.priority == Priority.HIGH:
                    priority = -100
                elif job.priority == Priority.NORMAL:
                    priority = -500
                elif job.priority == Priority.LOW:
                    priority = -1000
                else:
                    priority = -1000

                # TODO: Add a priority to the job...
                cmd = [
                    f"{settings.GRID_ENGINE_SUBMIT_CMD}",
                    "-p",
                    f"{priority}",
                    "-cwd",
                    f"{ftplus_path}/{settings.SCC_RUN_FILE}",
                ]
                logging.debug(cmd)

                # qsub must be run from inside job.uuid directory
                job_submit = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=ftplus_path
                )
                logging.debug(job_submit.stdout)

                # Assign SGE ID to job
                # Successful qsub stdout = Your job 6274206 ("ls -al") has been submitted
                sge_task_id = job_submit.stdout.split(" ")[2]
                job.sge_task_id = int(sge_task_id)
                job.save()
                JobLog.objects.create(job=job, event="Job sge_task_id added")

            except Exception as e:
                job.status = Status.ERROR
                job.save()
                msg = f"Job status changed to error. Exception: {e}"
                JobLog.objects.create(job=job, event=msg)
                logger.exception(msg)
        else:
            return

    except Job.DoesNotExist:
        logger.warning(f"Job {pk} does not exist")


@task(bind=True, ignore_result=True)
def delete_job(self: celery.Task, *, pk: typing.Union[str, uuid.UUID]):
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

        # Remove jobs-in-process dir created in activate_job
        ftplus_path = Path(settings.SCC_FTPLUS_PATH, "jobs-in-process", f"{job.uuid}")
        if ftplus_path.exists():
            subprocess.run(["rm", "-rf", f"{ftplus_path}"])

    except Job.DoesNotExist:
        logger.warning(f"Job {pk} does not exist")


def parse_qstat_output(output: str):
    """
    Takes output from qstat, captured by job_poll in scheduled_poll_job()
    Returns list of dictionaries. Each dict represents 1 row of qstat output
    That data is sent to update_jobs(), to update Job instances in web app
    """
    if "submit/start at" in output:
        output = output.replace("submit/start at", "submit-start-at")

    lines = [line for line in output.split("\n") if len(line)]
    header_keys = [column for column in lines[0].split(" ") if len(column)]

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
        if "@scc-" in row:
            data = {}
            for column in headers:
                start = headers[column]["start"]
                end = headers[column]["end"]
                if end:
                    data[column] = row[start:end].strip()
                else:
                    data[column] = row[start:].strip()
        rows.append(data)
    return rows


@task(bind=True, ignore_result=True, max_retries=0)
def scheduled_allocate_job(self: celery.Task) -> None:
    """
    Allocates existing Job instances to Celery at a set interval
    Interval determined by settings.CELERY_BEAT_SCHEDULE
    Should do so based on availability of different priority queues
    Availability based on settings.SCC_MAX_{priority}_JOBS
    """

    start = dt.now()
    # Look at how many jobs are Status.QUEUED, and Status.ACTIVE
    has_queued_jobs = bool(Job.objects.queued().exists())

    # Do we have any queued jobs ready to schedule?
    if has_queued_jobs:
        # Allocate *low* priority jobs
        active_jobs = Job.objects.exclude_imported().active()
        logger.info(f"{active_jobs.count()} jobs are active")

        queued_jobs = Job.objects.exclude_imported().queued()
        # queued_jobs = Job.objects.queued()
        logger.info(f"{queued_jobs.count()} jobs are queued")

        # if jobs_in_process < settings.SCC_MAX_LOW_JOBS:
        # jobs_to_allocate = 100
        # logger.info(f"{jobs_to_allocate} new jobs were allocated")
        for queued_job in queued_jobs.all():  # [:jobs_to_allocate]:
            logger.info(f"running activate_job(pk={queued_job.pk})")
            activate_job.delay(pk=queued_job.pk)

        # # Allocate *high* priority jobs
        # active_jobs = Job.objects.exclude_imported().high_priority().active()
        # queued_jobs = Job.objects.exclude_imported().high_priority().queued()
        # jobs_in_process = active_jobs.count()
        # logger.info(
        #     f"{jobs_in_process} of {settings.SCC_MAX_HIGH_JOBS} high priority jobs are active"
        # )

        # if jobs_in_process < settings.SCC_MAX_HIGH_JOBS:
        #     jobs_to_allocate = settings.SCC_MAX_HIGH_JOBS - jobs_in_process
        #     logger.info(f"{jobs_to_allocate} new high priority jobs were allocated")
        #     for queued_job in queued_jobs[:jobs_to_allocate]:
        #         activate_job.delay(pk=queued_job.pk)

        # # Allocate *normal* priority jobs
        # active_jobs = Job.objects.exclude_imported().normal_priority().active()
        # queued_jobs = Job.objects.exclude_imported().normal_priority().queued()
        # jobs_in_process = active_jobs.count()
        # logger.info(
        #     f"{jobs_in_process} of {settings.SCC_MAX_NORMAL_JOBS} normal priority jobs are active"
        # )

        # if jobs_in_process < settings.SCC_MAX_NORMAL_JOBS:
        #     jobs_to_allocate = settings.SCC_MAX_NORMAL_JOBS - jobs_in_process
        #     logger.info(f"{jobs_to_allocate} new medium priority jobs were allocated")
        #     for queued_job in queued_jobs[:jobs_to_allocate]:
        #         activate_job.delay(pk=queued_job.pk)

        # # Allocate *low* priority jobs
        # active_jobs = Job.objects.exclude_imported().low_priority().active()
        # queued_jobs = Job.objects.exclude_imported().low_priority().queued()
        # jobs_in_process = active_jobs.count()
        # logger.info(
        #     f"{jobs_in_process} of {settings.SCC_MAX_LOW_JOBS} low priority jobs are active"
        # )

        # if jobs_in_process < settings.SCC_MAX_LOW_JOBS:
        #     jobs_to_allocate = settings.SCC_MAX_LOW_JOBS - jobs_in_process
        #     logger.info(f"{jobs_to_allocate} new low priority jobs were allocated")
        #     for queued_job in queued_jobs[:jobs_to_allocate]:
        #         activate_job.delay(pk=queued_job.pk)

    stop = dt.now()
    logger.info(f"SCHEDULED_ALLOCATE_JOB took {(stop-start).seconds} seconds")


@task(bind=True, ignore_result=True, max_retries=0)
def scheduled_capture_job_output(self: celery.Task) -> None:
    """
    Periodically send TARed output directories from Status.COMPLETE & Status.ERROR jobs to web app
    Will also delete those directories from SCC
    Interval determined by settings.CELERY_BEAT_SCHEDULE
    Directory will be based on a setting
    """

    # We don't want imported jobs, jobs with no input file, or jobs with an output file
    capture_jobs = (
        Job.objects.exclude_imported()
        .exclude(
            input_file__in=["", None],
        )
        .filter(
            status__in=[Status.COMPLETE, Status.ERROR],
            output_file__in=["", None],
            last_exception_count__lt=10,
        )
    )

    for job in capture_jobs:
        logger.info(f"Processing Job: {job.uuid}")

        try:
            ftplus_path = Path(
                settings.SCC_FTPLUS_PATH, "jobs-in-process", f"{job.uuid}"
            )
            scc_job_input_file = f"{job.input_file.path}"
            logger.debug(scc_job_input_file)

            cmd = [
                "tar",
                "-czf",
                f"{scc_job_input_file}",
                "-C",
                f"{ftplus_path}",
                ".",
            ]

            logger.debug(f"File Retrival Command: {cmd}")

            # directory existence check
            if ftplus_path.exists():
                subprocess.run(cmd)
                scc_job_output_file = scc_job_input_file.replace(
                    "jobs_input", "jobs_output"
                )

                # Rename our input_file to match where we want our output_file to be
                Path(scc_job_input_file).rename(scc_job_output_file)

                job.output_file = scc_job_output_file.replace(
                    f"{settings.MEDIA_ROOT}", ""
                )
                job.save()

                # Delete SCC directory
                subprocess.run(["rm", "-rf", f"{ftplus_path}"])
            else:
                raise Exception(f"ftplus_path path: {ftplus_path} was not found")

        except Exception as e:
            msg = f"Job status changed to error. Exception: {e}"
            job.status = Status.ERROR
            job.last_exception = msg
            job.last_exception_at = timezone.now()
            job.last_exception_count = F("last_exception_count") + 1
            job.save()
            JobLog.objects.create(job=job, event=msg)
            logger.exception(msg)


@task(bind=True, ignore_result=True, max_retries=0)
def scheduled_cleanup_job(self: celery.Task, limit: int = 10_000) -> None:
    """
    To avoid overloading our database with old jobs, we cleanup all old jobs
    over, 7 days...
    """
    deleted_date = timezone.now() - timedelta(days=7)
    deleted_count, deleted_jobs = Job.objects.filter(
        pk__in=list(
            Job.objects.imported()
            .filter(created__lt=deleted_date)
            .order_by("created")
            .values_list("pk", flat=True)[:limit]
        )
    ).delete()
    logger.info(f"Deleted Jobs: {deleted_count}, {deleted_jobs}")


@task(bind=True, ignore_result=True, max_retries=0)
def scheduled_poll_job(self: celery.Task) -> None:
    """
    Checks status of current SCC jobs at a set interval
    Interval determined by settings.CELERY_BEAT_SCHEDULE

    Processing of those jobs will be handled by update_jobs()
    """

    start = dt.now()
    cmd = settings.GRID_ENGINE_STATUS_CMD.split(" ")
    if isinstance(cmd, list):
        job_poll = subprocess.run(cmd, capture_output=True, text=True)
    else:
        job_poll = subprocess.run([cmd], capture_output=True, text=True)

    # Capture qstat info as a list of dictionaries
    logger.debug(f"\nJOB_POLL.STDOUT{job_poll.stdout}")
    qstat_output = parse_qstat_output(job_poll.stdout)
    # Update jobs w/ qstat info
    logger.debug(f"\nQSTAT_OUTPUT{qstat_output}")

    update_start = dt.now()
    update_jobs(qstat_output)
    update_stop = dt.now()
    logger.info(f"UPDATE_JOBS took {(update_stop-update_start).seconds} seconds")

    stop = dt.now()
    logger.info(f"SCHEDULED_POLL_JOB took {(stop-start).seconds} seconds")


def update_jobs(qstat_output: str) -> None:
    """
    Takes input from scheduled_poll_job (a list of dictionaries)
    Parses that and saves the results to job objects in the web app
    Also updates Job.Status on jobs that have Errored or are complete
    Creation and processing of imported job objects is also handled here
    """

    user, created = User.objects.get_or_create(email=settings.SCC_DEFAULT_EMAIL)
    scc_job_list = []
    # Update all jobs w/ their qstat results
    for row in qstat_output:
        logger.debug(f"\nROW IS {row}")
        try:
            job_id = row["job-ID"]
            job_ja_task_id = (
                row.get("ja-task-ID") if len(row.get("ja-task-ID")) else None
            )
            # job_ja_task_id = (
            #     row.get("ja-task-ID")
            # )
            job_state = row["state"]
            job_submitted = f"{row['submit-start-at']}".replace("/", "-")
            job_submitted = parse(job_submitted)
            updated = False
    
            if job_submitted:
                job_submitted = pytz.timezone(settings.TIME_ZONE).localize(
                    job_submitted, is_dst=None
                )

            try:
                # Since BU doesn't care about imported jobs
                # Do we went to change this to ONLY update?
                # i see errors for multiple jobs submitted coming from here, i think we should test this without creating entries for non submitted jobs
                qs1 = Job.objects.queued()
                qs2 = Job.objects.active()
                scc_jobs = qs1.union(qs2)  #<- this would be before the loop
                ids = [x.sge_task_id for x in scc_jobs]  #<- before loop
                # if job_id in ids:
                #    job.job_data = row
                #    job.job_ja_task_id = job_ja_task_id
                #    job.job_state = job_state
                #    job.job_submitted = job_submitted
                #    job.scc_user = row.get("user")
                #    job.save()
                # can we do something like this to not get imported jobs?
                #job, created = Job.objects.get_or_create(
                #    sge_task_id=job_id,
                #    defaults={
                #        "imported": True,
                #        "job_data": row,
                #        "job_ja_task_id": job_ja_task_id,
                #        "job_state": job_state,
                #        "job_submitted": job_submitted,
                #        "status": Status.ACTIVE,
                #        "user": user,
                #    },
                #)
                #if not created:
                #    job.job_data = row
                #    job.job_ja_task_id = job_ja_task_id
                #    job.job_state = job_state
                #    job.job_submitted = job_submitted
                #    job.scc_user = row.get("user")
                #    job.save()
                scc_job_list.append(int(job_id)
                if job_id in ids:
                    job = Job.objects.get(sge_task_id=job_id)
                    job.job_data = row
                    job.job_ja_task_id = job_ja_task_id
                    job.job_state = job_state
                    job.job_submitted = job_submitted
                    job.scc_user = row.get("user")
                    job.save()
                    updated = True
                #job = Job.objects.get(sge_task_id=job_id)
                #job.job_data = row
                #job.job_ja_task_id = job_ja_task_id
                #job.job_state = job_state
                #job.job_submitted = job_submitted
                #job.scc_user = row.get("user")
                #job.save()

            except Job.MultipleObjectsReturned:
                logger.warning(f"Multiple jobs found for {job_id}")
                logger.debug(f"Deleting jobs for {job_id}")
                Job.objects.filter(sge_task_id=job_id).delete()

                #job, created = Job.objects.get_or_create(
                #    sge_task_id=job_id,
                #    defaults={
                #        "imported": True,
                #        "job_data": row,
                #        "job_ja_task_id": job_ja_task_id,
                #        "job_state": job_state,
                #        "job_submitted": job_submitted,
                #        "status": Status.ACTIVE,
                #        "user": user,
                #    },
                #)
                logger.debug(f"Creating new job {job_id} as {job.uuid}")

            # If an imported job is created, set to Status.ACTIVE & note it's imported
            # Error jobs will be updated later
            #if created:
            if updated:
                # Job.objects.filter(sge_task_id=job_id).update(
                #     imported=True, status=Status.ACTIVE
                # )
                #JobLog.objects.create(job=job, event="Imported job added to web app")
                JobLog.objects.create(job=job, event="Job updated with qstat info")
                
            else:
                #JobLog.objects.create(job=job, event="Job updated with qstat info")
                pass

            #scc_job_list.append(int(job_id))

        except Exception as e:
            logger.exception(f"Job {job_id} :: {e}")

    # Update status for Error jobs; will also catch imported Error jobs
    error_jobs = Job.objects.exclude(
        status__in=[
            Status.COMPLETE,
            Status.DELETED,
            Status.ERROR,
        ]
    ).filter(job_state="Eqw")
    for job in error_jobs:
        job.status = Status.ERROR
        job.save()
        JobLog.objects.create(
            job=job, event="Job status changed to error based on SCC's `Eqw` state"
        )

    # Update status of jobs that have been imported so they get out of our way
    Job.objects.imported().exclude(
        status__in=[
            Status.COMPLETE,
            Status.DELETED,
            Status.ERROR,
        ]
    ).update(status=Status.COMPLETE)

    # Update status for Complete jobs
    active_jobs = Job.objects.exclude_imported().active()
    # Completed SCC jobs show NO result in qstat
    logger.warning(scc_job_list)
    for job in active_jobs:
        if job.sge_task_id not in scc_job_list:
            job.status = Status.COMPLETE
            job.save()
            JobLog.objects.create(job=job, event="Job status changed to complete")

            # If our SCC_WEBHOOK_ENABLED settings is set to True, we
            # will fire off a webhook to a url when Jobs have been
            # successfully completed.
            if getattr(settings, "SCC_WEBHOOK_ENABLED", False):
                send_webhook.delay(pk=job.pk)


@task(bind=True, ignore_result=True)
def send_webhook(self: celery.Task, *, pk: typing.Union[str, uuid.UUID]):
    try:
        job = Job.objects.get(pk=pk)
        try:
            # build our webhook url
            url = settings.SCC_WEBHOOK_COMPLETED_JOB_URL.format(job.pk)
            msg = f"Sending Job {job.pk} to {url}"
            logging.info(msg)
            JobLog.objects.create(job=job, event=msg)

            # get our webhook auth token
            token_auth = TokenAuth(settings.SCC_WEBHOOK_COMPLETED_JOB_API_TOKEN)

            # prepare our data to JSON and send...
            job_serializer = JobSerializer(job)
            # job_serializer.is_valid()
            data = job_serializer.data

            if Path(job.output_file.path).exists():
                files = {
                    "ftmap_results_tar_file": Path(job.output_file.path).open("rb")
                }
            else:
                files = {}

            requests.post(url, auth=token_auth, data=data, files=files)
            requests.raise_for_status()

        except Exception as e:
            logger.warning(f"Job {pk} errored. {e}")

    except Job.DoesNotExist:
        logger.warning(f"Job {pk} does not exist. We can not send ")


@task(bind=True, ignore_result=True)
def update_job_priority(
    self: celery.Task, *, pk: typing.Union[str, uuid.UUID], new_priority: str
) -> None:
    """
    Update Job.priority
    Current assumption: 3 priority levels: Low/Normal/High
    Due to design changes, this task isn't in use at 2021-06-01
    It is tested by test_update_job_priority
    """
    try:
        job = Job.objects.get(pk=pk)
        job.priority = new_priority
        job.save()

        JobLog.objects.create(job=job, event=f"Job priority changed to {new_priority}")

    except Job.DoesNotExist:
        logger.warning(f"Job {pk} does not exist")
