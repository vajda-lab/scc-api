import pytest

from model_bakery import baker

from sccApi import models, serializers, tasks
from user_app.models import User


@pytest.mark.django_db()
def test_delete_job():
    """
    Tests task status properly updated by tasks.delete_job() 
    """
    job = baker.make("sccApi.Job",)
    assert job.status != models.Job.STATUS_DELETED
    tasks.delete_job(job.pk)
    job.refresh_from_db()
    assert job.status == models.Job.STATUS_DELETED

@pytest.mark.django_db()
def test_create_job():
    """
    Tests task status properly updated by tasks.create_job() 
    """
    job = baker.make("sccApi.Job",)
    assert job.status != models.Job.STATUS_ACTIVE
    tasks.create_job(job.pk)
    job.refresh_from_db()
    assert job.status == models.Job.STATUS_ACTIVE

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
def test_poll_job():
    result = tasks.poll_job()
    assert result