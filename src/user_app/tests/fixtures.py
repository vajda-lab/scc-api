import pytest


@pytest.fixture
def password():
    return "password"


@pytest.fixture
def staff(django_user_model, password):
    return django_user_model.objects.create_user(
        email="staff@here.com", password=password, is_staff=True
    )


@pytest.fixture
def superuser(django_user_model, password):
    return django_user_model.objects.create_user(
        email="superuser@here.com", password=password, is_superuser=True, is_staff=True
    )


@pytest.fixture
def user(django_user_model, password, **kwargs):
    email = kwargs.pop("email", "user@here.com")
    return django_user_model.objects.create_user(
        email=email, password=password, **kwargs
    )
