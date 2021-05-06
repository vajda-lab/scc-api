import pytest

from ..models import Priority, Status


@pytest.mark.django_db()
def test_job_model_defaults(job):
    assert job.priority == Priority.LOW
    assert job.status == Status.QUEUED


@pytest.mark.django_db()
def test_job_log_model_defaults(job_log):
    assert job_log.created
