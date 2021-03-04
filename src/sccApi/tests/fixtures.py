import pytest

from model_bakery import baker


@pytest.fixture
def job(user):
    return baker.make("sccApi.Job", user=user)
