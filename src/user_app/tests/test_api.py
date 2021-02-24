import pytest

from model_bakery import baker

from user_app import models, serializers


# Test User List url
@pytest.mark.django_db()
def test_user_list_url(tp, user):
    expected_url = "/apis/users/"
    reversed_url = tp.reverse("user-list")
    assert expected_url == reversed_url


@pytest.mark.django_db()
def test_user_list(tp, user):
    """
    GET '/apis/users/'
    2nd assert is an extra check
    """
    url = tp.reverse("user-list")
    response = tp.get_check_200(url)
    results = response.data["results"]
    assert len(results) == 1

    result = results[0]
    assert user.pk == result["pk"]


@pytest.mark.django_db()
def test_user_create(tp):
    """
    POST '/apis/users/'
    """
    url = tp.reverse("user-list")
    user = baker.prepare("user_app.User")
    payload = serializers.UserSerializer(instance=user).data
    del payload["pk"]
    response = tp.client.post(url, data=payload, content_type="application/json")

    pk = response.json()["pk"]
    tp.response_201(response)

    user_obj = models.User.objects.get(pk=pk)
    assert user_obj.pk


# Test User Detail url
@pytest.mark.django_db()
def test_user_detail_url(tp, user):
    expected_url = f"/apis/users/{user.pk}/"
    reversed_url = tp.reverse("user-detail", pk=user.pk)
    assert expected_url == reversed_url


@pytest.mark.django_db()
def test_user_detail(tp, user):
    """
    GET '/apis/users/{pk}/'
    """
    url = tp.reverse("user-detail", pk=user.pk)
    response = tp.get_check_200(url)
    assert "pk" in response.data
    assert user.pk == response.data["pk"]


@pytest.mark.django_db()
def test_user_delete(tp):
    """
    DELETE '/apis/users/{pk}/'
    """
    user = baker.make("user_app.User")
    url = tp.reverse("user-detail", pk=user.pk)
    response = tp.client.delete(url, content_type="application/json")
    tp.response_204(response)
    assert models.User.objects.filter(pk=user.pk).count() == 0


@pytest.mark.django_db()
def test_user_partial_update(tp, user):
    """
    PATCH '/apis/users/{pk}'
    """
    new_organization = "new-organization"
    assert user.organization is not new_organization
    url = tp.reverse("user-detail", pk=user.pk)
    payload = {"organization": new_organization}
    response = tp.client.patch(url, data=payload, content_type="application/json")
    tp.response_200(response)

    user_obj = models.User.objects.get(pk=user.pk)
    assert user_obj.organization == new_organization


@pytest.mark.django_db()
def test_user_update(tp, user):
    """
    PUT '/apis/users/{pk}/'
    """
    new_organization = "new-organization"
    assert user.organization is not new_organization

    url = tp.reverse("user-detail", pk=user.pk)
    payload = serializers.UserSerializer(instance=user).data
    payload["organization"] = new_organization
    response = tp.client.put(url, data=payload, content_type="application/json")
    tp.response_200(response)

    user_obj = models.User.objects.get(pk=user.pk)
    assert user_obj.organization == new_organization
