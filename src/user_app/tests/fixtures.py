import pytest

from model_bakery import baker


@pytest.fixture
def user():
    return baker.make("user_app.User")
