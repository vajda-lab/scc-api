import pytest

from model_bakery import baker


@pytest.fixture
def job(user):
    return baker.make("jobs.Job", user=user)


@pytest.fixture
def job_log(job):
    return baker.make("jobs.JobLog", job=job)
