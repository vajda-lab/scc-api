import pytest

from ..models import Priority, Status


@pytest.mark.django_db()
def test_model_defaults(job):
    assert job.priority == Priority.LOW
    assert job.status == Status.QUEUED
