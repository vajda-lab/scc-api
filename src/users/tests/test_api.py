import pytest
from rest_framework.authtoken.models import Token

from model_bakery import baker

from users import models, serializers


# Test User List url
@pytest.mark.django_db()
def test_user_list_url(tp, user):
    expected_url = "/apis/users/"
    reversed_url = tp.reverse("user-list")
    assert expected_url == reversed_url


@pytest.mark.django_db()
def test_user_list(tp, user, password):
    """
    GET '/apis/users/'
    2nd assert is an extra check
    """
    url = tp.reverse("user-list")

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()

    # Does API work with auth?
    tp.client.login(email=user.email, password=password)
    response = tp.get_check_200(url)
    results = response.data["results"]
    assert len(results) == 1

    result = results[0]
    assert user.pk == result["pk"]


@pytest.mark.django_db()
def test_user_create(tp, user, password):
    """
    POST '/apis/users/'
    """
    url = tp.reverse("user-list")
    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()

    new_user = baker.prepare("users.User")
    # Does API work with auth?
    tp.client.login(email=user.email, password=password)
    payload = serializers.UserSerializer(instance=new_user).data
    del payload["pk"]
    response = tp.client.post(url, data=payload, content_type="application/json")

    pk = response.json()["pk"]
    tp.response_201(response)

    user_obj = models.User.objects.get(pk=pk)
    user_token = Token.objects.get(user=user_obj)
    assert user_obj.pk
    assert user_token


# Test User Detail url
@pytest.mark.django_db()
def test_user_detail_url(tp, user):
    expected_url = f"/apis/users/{user.pk}/"
    reversed_url = tp.reverse("user-detail", pk=user.pk)
    assert expected_url == reversed_url


@pytest.mark.django_db()
def test_user_detail(tp, user, password):
    """
    GET '/apis/users/{pk}/'
    """
    url = tp.reverse("user-detail", pk=user.pk)

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()

    # Does API work with auth?
    tp.client.login(email=user.email, password=password)
    response = tp.get_check_200(url)
    assert "pk" in response.data
    assert user.pk == response.data["pk"]


@pytest.mark.django_db()
def test_user_delete(tp, user, password):
    """
    DELETE '/apis/users/{pk}/'
    """
    new_user = baker.make("users.User")
    url = tp.reverse("user-detail", pk=new_user.pk)

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()

    # Does API work with auth?
    tp.client.login(email=user.email, password=password)
    response = tp.client.delete(url, content_type="application/json")
    tp.response_204(response)
    assert models.User.objects.filter(pk=new_user.pk).count() == 0


@pytest.mark.django_db()
def test_user_partial_update(tp, user, password):
    """
    PATCH '/apis/users/{pk}'
    """
    new_name = "Jacob Lyons"
    assert user.full_name is not new_name
    url = tp.reverse("user-detail", pk=user.pk)
    payload = {"full_name": new_name}

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()

    # Does API work with auth?
    tp.client.login(email=user.email, password=password)
    response = tp.client.patch(url, data=payload, content_type="application/json")
    tp.response_200(response)

    user_obj = models.User.objects.get(pk=user.pk)
    assert user_obj.full_name == new_name


@pytest.mark.django_db()
def test_user_update(tp, user, password):
    """
    PUT '/apis/users/{pk}/'
    """
    new_name = "Jacob Lyons"
    assert user.full_name is not new_name

    url = tp.reverse("user-detail", pk=user.pk)
    payload = serializers.UserSerializer(instance=user).data
    payload["full_name"] = new_name

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()

    # Does API work with auth?
    tp.client.login(email=user.email, password=password)
    response = tp.client.put(url, data=payload, content_type="application/json")
    tp.response_200(response)

    user_obj = models.User.objects.get(pk=user.pk)
    assert user_obj.full_name == new_name
