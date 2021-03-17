import pytest

from model_bakery import baker

from sccApi import models, serializers, tasks
from user_app.models import User


@pytest.mark.django_db()
def test_delete_job():
    """
    # ToDo UPDATE DOCSTRING
    """
    job = baker.make("sccApi.Job",)
    assert job.status is not models.Job.STATUS_DELETED
    tasks.delete_job(job.pk)
    job.refresh_from_db()
    assert job.status == models.Job.STATUS_DELETED

@pytest.mark.django_db()
def test_create_job():
    pass

@pytest.mark.django_db()
def test_update_job_priority():
    pass

@pytest.mark.django_db()
def test_poll_job():
    pass