import pytest

from model_bakery import baker
from pathlib import Path

from sccApi import tasks
from sccApi.models import Job, Priority, Status


@pytest.mark.django_db()
def test_activate_job():
    """
    Tests task status properly updated by tasks.activate_job()
    """
    job = baker.make(
        "sccApi.Job",
    )
    assert job.status != Status.ACTIVE
    qsub_response = tasks.activate_job(pk=job.pk)
    job.refresh_from_db()
    assert job.status == Status.ACTIVE
    assert qsub_response.returncode == 0
    assert "5290723" in qsub_response.stdout
    assert "has been submitted" in qsub_response.stdout


@pytest.mark.django_db()
def test_delete_job():
    """
    Tests task status properly updated by tasks.delete_job()
    """
    job = baker.make(
        "sccApi.Job",
    )
    assert job.status != Status.DELETED
    qdel_response = tasks.delete_job(pk=job.pk)
    job.refresh_from_db()
    assert job.status == Status.DELETED
    assert qdel_response.returncode == 0
    assert b"5290728.1" in qdel_response.stdout
    assert b"5290728.2" in qdel_response.stdout
    assert b"has registered the job" in qdel_response.stdout
    assert b"for deletion" in qdel_response.stdout


@pytest.mark.django_db()
def test_update_job_priority():
    """
    Tests task priority properly updated by tasks.update_job_priority

    Current assumption: 3 priority levels: Low/Normal/High
    """
    job = baker.make(
        "sccApi.Job",
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


# @pytest.mark.django_db()
# def test_scheduled_poll_job():
#     # TODO: This command requires an --option to be passed in
#     qstat_response = tasks.scheduled_poll_job()
#     assert qstat_response[1] == 0

#     # Testing options in qstat mock
#     if len(qstat_response[0]) > 1:
#         if qstat_response[0][1] == '-u':
#             assert b"5290728" in qstat_response[2]
#         else:
#             assert b"job_number:                 5290723" in qstat_response[2]


@pytest.mark.django_db()
def test_scheduled_allocate_job():
    baker.make("sccApi.Job", status=Status.QUEUED, _quantity=2)

    assert Job.objects.filter(status=Status.QUEUED).count() == 2
    assert Job.objects.filter(status=Status.ACTIVE).count() == 0

    tasks.scheduled_allocate_job()

    assert Job.objects.filter(status=Status.QUEUED).count() == 0
    assert Job.objects.filter(status=Status.ACTIVE).count() == 2


@pytest.mark.django_db()
def test_scheduled_capture_job_output():
    # Create jobs with and without output files and appropriate statuses
    error_job = baker.make(
        "sccApi.Job", status=Status.ERROR, sge_task_id=1, output_file=None
    )
    complete_job = baker.make(
        "sccApi.Job", status=Status.COMPLETE, sge_task_id=9, output_file=None
    )

    ignore_me_job = baker.make(
        "sccApi.Job",
        status=Status.ERROR,
        sge_task_id=10,
        output_file="i_had_errors.tar.gz",
    )
    ignore_me_too_job = baker.make(
        "sccApi.Job",
        status=Status.COMPLETE,
        sge_task_id=90,
        output_file="i_am_done.tar.gz",
    )

    # Setup directories to compress/attach
    tasks.scheduled_capture_job_output()

    assert error_job.output_file != None
    print(f"error_job.output_file: {error_job.output_file}")
    assert complete_job.output_file != None
    print(f"complete_job.output_file: {complete_job.output_file}")
    assert ignore_me_job.output_file == "i_had_errors.tar.gz"
    assert ignore_me_too_job.output_file == "i_am_done.tar.gz"


@pytest.mark.django_db()
def test_parse_qstat_output():
    """
    Tests parse_qstat_output task.
    """

    # NOTE: input_filename & input_buffer are mocks
    input_filename = "/app/sccApi/tests/qstat_test_output.txt"
    if Path(input_filename).exists():
        input_buffer = Path(input_filename).read_text()
        input_buffer = input_buffer.replace("submit/start at", "submit-start-at")
    else:
        print(f"\nNo Such File as {input_filename} in {Path.cwd()}")

    qstat_rows = tasks.parse_qstat_output(input_buffer)
    assert len(qstat_rows) > 1
    print (qstat_rows[:2])


@pytest.mark.django_db()
def test_update_jobs():
    # Job names are their intended FINAL state
    error_job = baker.make("sccApi.Job", status=Status.ACTIVE, sge_task_id=1)
    complete_job = baker.make("sccApi.Job", status=Status.ACTIVE, sge_task_id=9)

    # waves hands
    qstat_output = {}

    tasks.update_jobs(qstat_output)
    assert error_job.status == Status.ERROR
    assert error_job.job_state == "Eqw"
    assert complete_job.status == Status.COMPLETE
