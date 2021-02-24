import pytest

from model_bakery import baker


@pytest.fixture
def job():
    return baker.make("sccApi.Job")
