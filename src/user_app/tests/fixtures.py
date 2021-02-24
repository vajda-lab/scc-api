import pytest

from model_bakery import baker


@pytest.fixture
def user():
    return baker.make("user_app.User")


@pytest.fixture
def superuser():
    return baker.make("user_app.User", is_superuser=True, is_staff=True)


@pytest.fixture
def staff():
    return baker.make("user_app.User", is_staff=True)
