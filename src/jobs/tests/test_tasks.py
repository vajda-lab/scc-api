import pytest
import tempfile
import time_machine

from datetime import timedelta
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from model_bakery import baker
from pathlib import Path

from jobs import tasks
from jobs.models import Job, JobLog, Priority, Status


@pytest.mark.django_db()
def test_activate_job():
    """
    Tests task status properly updated by tasks.activate_job()
    """
    job = baker.make(
        "jobs.Job",
        input_file=SimpleUploadedFile(
            "test-job.tar.gz",
            Path(__file__).parent.joinpath("test-job.tar.gz").read_bytes(),
        ),
    )
    assert job.status != Status.ACTIVE
    tasks.activate_job(pk=job.pk)
    job.refresh_from_db()
    assert job.status == Status.ACTIVE


@pytest.mark.django_db()
def test_delete_job():
    """
    Tests task status properly updated by tasks.delete_job()
    """
    job = baker.make(
        "jobs.Job",
    )
    assert job.status != Status.DELETED
    tasks.delete_job(pk=job.pk)
    job.refresh_from_db()
    assert job.status == Status.DELETED


@pytest.mark.django_db()
def test_update_job_priority():
    """
    Tests task priority properly updated by tasks.update_job_priority

    Current assumption: 3 priority levels: Low/Normal/High
    """
    job = baker.make(
        "jobs.Job",
    )
    # 0 or Low is the default value
    assert job.priority == Priority.LOW
    # Update to High
    tasks.update_job_priority(pk=job.pk, new_priority=Priority.HIGH)
    job.refresh_from_db()
    assert job.priority == Priority.HIGH
    # Update to Normal
    tasks.update_job_priority(pk=job.pk, new_priority=Priority.NORMAL)
    job.refresh_from_db()
    assert job.priority == Priority.NORMAL


@pytest.mark.django_db()
def test_scheduled_allocate_job():
    baker.make(
        "jobs.Job",
        input_file=SimpleUploadedFile(
            "test-job.tar.gz",
            Path(__file__).parent.joinpath("test-job.tar.gz").read_bytes(),
        ),
        status=Status.QUEUED,
        _quantity=2,
    )

    assert Job.objects.filter(status=Status.QUEUED).count() == 2
    assert Job.objects.filter(status=Status.ACTIVE).count() == 0
    assert JobLog.objects.count() == 0

    tasks.scheduled_allocate_job()

    assert Job.objects.filter(status=Status.QUEUED).count() == 0
    assert Job.objects.filter(status=Status.ACTIVE).count() == 2
    assert JobLog.objects.count() == 4


@pytest.mark.xfail
@pytest.mark.django_db()
def test_scheduled_capture_job_output():
    # Create jobs with and without output files and appropriate statuses
    error_job = baker.make(
        "jobs.Job", status=Status.ERROR, sge_task_id=1, output_file=None
    )
    complete_job = baker.make(
        "jobs.Job", status=Status.COMPLETE, sge_task_id=9, output_file=None
    )

    ignore_me_job = baker.make(
        "jobs.Job",
        status=Status.ERROR,
        sge_task_id=10,
        output_file=tempfile.NamedTemporaryFile(suffix=".tar.gz").name,
    )
    ignore_me_too_job = baker.make(
        "jobs.Job",
        status=Status.COMPLETE,
        sge_task_id=90,
        output_file=tempfile.NamedTemporaryFile(suffix=".tar.gz").name,
    )

    assert Job.objects.all().count() == 4
    # Setup directories to compress/attach
    # Decide where to put temporary files

    tasks.scheduled_capture_job_output()

    assert error_job.output_file.name != ""
    assert complete_job.output_file != ""
    assert ignore_me_job.output_file
    assert ignore_me_too_job.output_file


@override_settings(SCC_DELETE_OLD_JOBS_IN_DAYS=30)
@pytest.mark.django_db()
def test_scheduled_cleanup_job():
    baker.make("jobs.Job", _quantity=2)

    with time_machine.travel(
        timezone.now() - timedelta(days=settings.SCC_DELETE_OLD_JOBS_IN_DAYS)
    ):
        baker.make("jobs.Job", imported=True)

    assert Job.objects.all().count() == 3

    tasks.scheduled_cleanup_job()

    assert Job.objects.all().count() == 2


#@pytest.mark.django_db()
def test_parse_qstat_output():
    """
    Tests parse_qstat_output task.
    """

    # NOTE: input_filename & input_buffer: TEST MOCKS BEFORE CONTAINER ISSUES SORTED
    input_filename = Path(__file__).parent.joinpath("qstat_test_output.txt")
    input_buffer = input_filename.read_text()
    qstat_rows = tasks.parse_qstat_output(input_buffer)
    assert len(qstat_rows) > 1
    assert qstat_rows[1]["job-ID"].strip() == "6260963"
    assert qstat_rows[1]["state"].strip() == "r"
    assert qstat_rows[-1]["job-ID"].strip() == "6262064"
    assert qstat_rows[-1]["state"].strip() == "r"


@pytest.mark.django_db()
def test_update_jobs():
    """
    Tests tasks.update_jobs

    qstat_output[0] should convert error_job from Status.ACTIVE to Status.ERROR
    qstat_output[1] should create a new job w/ Status.ACTIVE
    qstat_output[2] should create a new job w/ Status.ERROR
    qstat_output[3] should create a new job w/ Status.ACTIVE and blank ja-task-ID
    complete_job should convert from Status.ACTIVE to Status.COMPLETE
    """

    # Job names are their intended FINAL state
    error_job = baker.make("jobs.Job", status=Status.ACTIVE, sge_task_id=1)
    complete_job = baker.make("jobs.Job", status=Status.ACTIVE, sge_task_id=9)

    # MOCK INPUT FOR TEST BEFORE CONTAINER ISSUES SORTED
    qstat_output = [
        {
            "job-ID": "1",
            "prior": "0.10000",
            "name": "nf-analysi",
            "user": "xrzhou",
            "state": "Eqw",
            "submit-start-at": "04/28/2021 19:32:38",
            "queue": "linga@scc-kb3.scc.bu.edu",
            "slots": "1",
            "ja-task-ID": "11",
        },
        {
            "job-ID": "6260963",
            "prior": "0.10000",
            "name": "nf-analysi",
            "user": "xrzhou",
            "state": "r",
            "submit-start-at": "04/28/2021 19:33:25",
            "queue": "linga@scc-kb8.scc.bu.edu",
            "slots": "1",
            "ja-task-ID": "19",
        },
        {
            "job-ID": "4260964",
            "prior": "0.10000",
            "name": "nf-analysi",
            "user": "xrzhou",
            "state": "Eqw",
            "submit-start-at": "04/28/2021 19:32:38",
            "queue": "linga@scc-kb3.scc.bu.edu",
            "slots": "1",
            "ja-task-ID": "11",
        },
        {
            "job-ID": "6260964",
            "prior": "0.10000",
            "name": "nf-analysi",
            "user": "xrzhou",
            "state": "r",
            "submit-start-at": "04/28/2021 19:33:25",
            "queue": "linga@scc-kb8.scc.bu.edu",
            "slots": "1",
            "ja-task-ID": "",
        },
    ]

    tasks.update_jobs(qstat_output)
    error_job.refresh_from_db()
    # error_job tests
    assert error_job.status == Status.ERROR
    assert error_job.job_state == "Eqw"
    # Were correct new objects created for the imported jobs?
    assert Job.objects.get(sge_task_id=6260963)
    assert Job.objects.get(sge_task_id=6260963).status == Status.COMPLETE
    assert Job.objects.get(sge_task_id=4260964)
    assert Job.objects.get(sge_task_id=4260964).status == Status.ERROR
    # Was complete_job's status changed?
    complete_job.refresh_from_db()
    assert complete_job.status == Status.COMPLETE
    assert len(Job.objects.all()) == 5
