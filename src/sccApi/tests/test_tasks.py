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
    # 0 or normal is the default value
    print(f"\nJOB.PRIORITY is {job.priority}")
    assert job.priority == 0
    # Update to High
    tasks.update_job_priority(job.pk, 1)
    job.refresh_from_db()
    print(f"\nJOB.PRIORITY is {job.priority}")
    assert job.priority == 1
    # Update to Low
    tasks.update_job_priority(job.pk, -1)
    job.refresh_from_db()
    print(f"\nJOB.PRIORITY is {job.priority}")
    assert job.priority == -1

@pytest.mark.django_db()
def test_poll_job():
    result = tasks.poll_job()
    assert result