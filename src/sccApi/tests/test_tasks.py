import pytest

from model_bakery import baker

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
