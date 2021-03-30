import pytest

from model_bakery import baker

from sccApi import models, serializers, tasks
from user_app.models import User


@pytest.mark.django_db()
def test_create_job():
    """
    Tests task status properly updated by tasks.create_job() 
    """
    job = baker.make("sccApi.Job",)
    assert job.status != models.Job.STATUS_ACTIVE
    qsub_response = tasks.create_job(job.pk)
    job.refresh_from_db()
    assert job.status == models.Job.STATUS_ACTIVE
    assert qsub_response.returncode == 0
    assert b"5290723" in qsub_response.stdout
    assert b"has been submitted" in qsub_response.stdout

@pytest.mark.django_db()
def test_delete_job():
    """
    Tests task status properly updated by tasks.delete_job() 
    """
    job = baker.make("sccApi.Job",)
    assert job.status != models.Job.STATUS_DELETED
    qdel_response = tasks.delete_job(job.pk)
    job.refresh_from_db()
    assert job.status == models.Job.STATUS_DELETED
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
    job = baker.make("sccApi.Job",)
    # 0 or Low is the default value
    assert job.priority == models.Priority.LOW
    # Update to High
    tasks.update_job_priority(job.pk, models.Priority.HIGH)
    job.refresh_from_db()
    assert job.priority == models.Priority.HIGH
    # Update to Normal
    tasks.update_job_priority(job.pk, models.Priority.NORMAL)
    job.refresh_from_db()
    assert job.priority == models.Priority.NORMAL

@pytest.mark.django_db()
def test_scheduled_poll_job():
    # TODO: This command requires an --option to be passed in
    qstat_response = tasks.scheduled_poll_job()
    assert qstat_response.returncode == 2
