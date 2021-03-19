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

    Current assumption: only 2 priority levels: Normal and High 
    """
    job = baker.make("sccApi.Job",)
    # False is the default value
    assert job.priority == False
    tasks.update_job_priority(job.pk)
    job.refresh_from_db()
    assert job.priority == True
    # Does it work both ways?
    tasks.update_job_priority(job.pk)
    job.refresh_from_db()
    assert job.priority == False

@pytest.mark.django_db()
def test_poll_job():
    result = tasks.poll_job()
    assert result