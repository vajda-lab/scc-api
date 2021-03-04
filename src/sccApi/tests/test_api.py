import pytest

from model_bakery import baker

from sccApi import models, serializers
from user_app.models import User


# Test Job List url
@pytest.mark.django_db()
def test_job_list_url(tp, job):
    expected_url = "/apis/jobs/"
    reversed_url = tp.reverse("job-list")
    assert expected_url == reversed_url


@pytest.mark.django_db()
def test_job_list(tp, job, user, password):
    """
    GET '/apis/jobs/'
    2nd assert is an extra check
    """
    url = tp.reverse("job-list")

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()

    # Does API work with auth?
    tp.client.login(email=user.email, password=password)
    response = tp.get_check_200(url)
    results = response.data["results"]
    assert len(results) == 1

    result = results[0]
    assert str(job.pk) == result["uuid"]


@pytest.mark.django_db()
def test_job_create(tp, user, password):
    """
    POST '/apis/jobs/'
    """
    url = tp.reverse("job-list")

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()

    # Does API work with auth?
    tp.client.login(email=user.email, password=password)

    job = baker.prepare("sccApi.Job", user=user)
    payload = serializers.JobSerializer(instance=job).data
    del payload["uuid"]
    response = tp.client.post(url, data=payload, content_type="application/json")

    pk = response.json()["uuid"]
    tp.response_201(response)

    job_obj = models.Job.objects.get(pk=pk)
    assert job_obj.pk


# Test Job Detail url
@pytest.mark.django_db()
def test_job_detail_url(tp, job):
    expected_url = f"/apis/jobs/{job.pk}/"
    reversed_url = tp.reverse("job-detail", pk=job.pk)
    assert expected_url == reversed_url


@pytest.mark.django_db()
def test_job_detail(tp, job, user, password):
    """
    GET '/apis/jobs/{pk}/'
    """
    url = tp.reverse("job-detail", pk=job.pk)

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()

    # Does API work with auth?
    tp.client.login(email=user.email, password=password)

    response = tp.get_check_200(url)
    assert "uuid" in response.data
    assert str(job.pk) == response.data["uuid"]


@pytest.mark.django_db()
def test_job_delete(tp, user, password):
    """
    DELETE '/apis/jobs/{pk}/'
    """
    job = baker.make("sccApi.Job", user=user)
    url = tp.reverse("job-detail", pk=job.pk)

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()

    # Does API work with auth?
    tp.client.login(email=user.email, password=password)
    response = tp.client.delete(url, content_type="application/json")
    tp.response_204(response)
    assert models.Job.objects.filter(pk=job.pk).count() == 0


    job = baker.make("sccApi.Job", user=user)
    url = tp.reverse("job-detail", pk=job.pk)

    new_user = baker.make("user_app.User", password=password, is_superuser=False)
    # Does API work with auth?
    tp.client.login(email=new_user.email, password=password)
    response = tp.client.delete(url, content_type="application/json")
    tp.response_204(response)
    assert models.Job.objects.filter(pk=job.pk).count() == 0


@pytest.mark.django_db()
def test_job_partial_update(tp, job, user, password):
    """
    PATCH '/apis/jobs/{pk}'
    """
    new_status = job.STATUS_ERROR
    assert job.status is not new_status
    url = tp.reverse("job-detail", pk=job.pk)

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()

    # Does API work with auth?
    tp.client.login(email=user.email, password=password)
    payload = {"status": new_status}
    response = tp.client.patch(url, data=payload, content_type="application/json")
    tp.response_200(response)

    job_obj = models.Job.objects.get(pk=job.pk)
    assert job_obj.status == new_status


@pytest.mark.django_db()
def test_job_update(tp, job, user, password):
    """
    PUT '/apis/jobs/{pk}/'
    """
    new_status = job.STATUS_ERROR
    assert job.status is not new_status

    url = tp.reverse("job-detail", pk=job.pk)

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()

    # Does API work with auth?
    tp.client.login(email=user.email, password=password)
    payload = serializers.JobSerializer(instance=job).data
    payload["status"] = new_status
    response = tp.client.put(url, data=payload, content_type="application/json")
    tp.response_200(response)

    job_obj = models.Job.objects.get(pk=job.pk)
    assert job_obj.status == new_status
