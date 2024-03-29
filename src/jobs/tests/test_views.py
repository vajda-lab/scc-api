import pytest

from model_bakery import baker

from jobs import models, serializers


# The noauth tests can probably get grouped in a class
# I'll have to look up how to do that
@pytest.mark.django_db()
def test_job_list_url(tp, job):
    expected_url = "/apis/jobs/"
    reversed_url = tp.reverse("apis:job-list")
    assert expected_url == reversed_url


def test_job_list_noauth(tp, job):
    """
    GET '/apis/jobs/'
    """
    url = tp.reverse("apis:job-list")

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "test_user,expected",
    [
        (pytest.lazy_fixture("user"), 200),
        (pytest.lazy_fixture("staff"), 200),
        (pytest.lazy_fixture("superuser"), 200),
    ],
)
def test_job_list(tp, job, password, test_user, expected):
    """
    GET '/apis/jobs/'
    """
    url = tp.reverse("apis:job-list")

    tp.client.login(email=test_user.email, password=password)

    response = tp.get(url)
    assert response.status_code == expected

    results = response.data["results"]
    assert len(results) == 1

    result = results[0]
    assert str(job.pk) == result["uuid"]


def test_job_create_noauth(tp):
    """
    POST '/apis/jobs/'
    """
    url = tp.reverse("apis:job-list")

    # Without auth, API should return 401
    tp.post(url)
    tp.response_401()


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "test_user,http_status",
    [
        (pytest.lazy_fixture("user"), 201),
        (pytest.lazy_fixture("staff"), 201),
        (pytest.lazy_fixture("superuser"), 201),
    ],
)
def test_job_create(tp, password, test_user, http_status):
    """
    POST '/apis/jobs/'
    """
    url = tp.reverse("apis:job-list")

    # Can users create jobs?
    tp.client.login(email=test_user.email, password=password)

    job = baker.prepare("jobs.Job", user=test_user)
    payload = serializers.JobSerializer(instance=job).data
    del payload["uuid"]
    response = tp.client.post(url, data=payload, content_type="application/json")
    pk = response.json()["uuid"]

    # Was job created?
    assert response.status_code == http_status
    job_obj = models.Job.objects.get(pk=pk)
    assert job_obj.pk


# Test Job Detail url
@pytest.mark.django_db()
def test_job_detail_url(tp, job):
    expected_url = f"/apis/jobs/{job.pk}/"
    reversed_url = tp.reverse("apis:job-detail", pk=job.pk)
    assert expected_url == reversed_url


def test_job_detail_noauth(tp, job):
    """
    GET '/apis/jobs/{pk}/'
    """
    url = tp.reverse("apis:job-detail", pk=job.pk)

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "test_user",
    [
        (pytest.lazy_fixture("user")),
        (pytest.lazy_fixture("staff")),
        (pytest.lazy_fixture("superuser")),
    ],
)
def test_job_detail(tp, job, password, test_user):
    """
    GET '/apis/jobs/{pk}/'
    """
    url = tp.reverse("apis:job-detail", pk=job.pk)

    # Can users see job detail?
    tp.client.login(email=test_user.email, password=password)

    response = tp.get_check_200(url)
    assert "uuid" in response.data
    assert str(job.pk) == response.data["uuid"]


def test_job_delete_noauth(tp, user):
    """
    DELETE '/apis/jobs/{pk}/'
    """
    job = baker.make("jobs.Job", user=user)
    url = tp.reverse("apis:job-detail", pk=job.pk)

    # Without auth, API should return 401
    tp.delete(url)
    tp.response_401()


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "creating_user,deleting_user,http_status,expected_jobs",
    [
        (pytest.lazy_fixture("user"), pytest.lazy_fixture("user"), 204, 0),
        (pytest.lazy_fixture("user"), pytest.lazy_fixture("staff"), 204, 0),
        (pytest.lazy_fixture("user"), pytest.lazy_fixture("superuser"), 204, 0),
        (pytest.lazy_fixture("staff"), pytest.lazy_fixture("user"), 404, 1),
        (pytest.lazy_fixture("staff"), pytest.lazy_fixture("staff"), 204, 0),
        (pytest.lazy_fixture("staff"), pytest.lazy_fixture("superuser"), 204, 0),
        (pytest.lazy_fixture("superuser"), pytest.lazy_fixture("user"), 404, 1),
        (pytest.lazy_fixture("superuser"), pytest.lazy_fixture("staff"), 404, 1),
        (pytest.lazy_fixture("superuser"), pytest.lazy_fixture("superuser"), 204, 0),
    ],
)
def test_job_delete(
    tp, password, creating_user, deleting_user, http_status, expected_jobs
):
    """
    DELETE '/apis/jobs/{pk}/'
    Can a creating_user job be deleted by deleting_user?
    """
    job = baker.make("jobs.Job", user=creating_user)
    url = tp.reverse("apis:job-detail", pk=job.pk)

    # Can another user delete this job?
    tp.client.login(email=deleting_user.email, password=password)
    response = tp.client.delete(url, content_type="application/json")
    assert response.status_code == http_status

    # Do we have the correct number of jobs, after delete attempt
    assert (
        models.Job.objects.filter(pk=job.pk)
        .exclude(status=models.Status.DELETED)
        .count()
        == expected_jobs
    )


def test_job_partial_update_noauth(tp, job):
    """
    PATCH '/apis/jobs/{pk}/'
    """
    url = tp.reverse("apis:job-detail", pk=job.pk)

    # Without auth, API should return 401
    tp.patch(url)
    tp.response_401()


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "creating_user,patching_user,http_status, exp_job_status",
    [
        (pytest.lazy_fixture("user"), pytest.lazy_fixture("user"), 200, "error"),
        (pytest.lazy_fixture("user"), pytest.lazy_fixture("staff"), 200, "error"),
        (pytest.lazy_fixture("user"), pytest.lazy_fixture("superuser"), 200, "error"),
        (pytest.lazy_fixture("staff"), pytest.lazy_fixture("user"), 404, "queued"),
        (pytest.lazy_fixture("staff"), pytest.lazy_fixture("staff"), 200, "error"),
        (pytest.lazy_fixture("staff"), pytest.lazy_fixture("superuser"), 200, "error"),
        (pytest.lazy_fixture("superuser"), pytest.lazy_fixture("user"), 404, "queued"),
        (pytest.lazy_fixture("superuser"), pytest.lazy_fixture("staff"), 404, "queued"),
        (
            pytest.lazy_fixture("superuser"),
            pytest.lazy_fixture("superuser"),
            200,
            "error",
        ),
    ],
)
def test_job_partial_update(
    tp, password, creating_user, patching_user, http_status, exp_job_status
):
    """
    PATCH '/apis/jobs/{pk}/'
    Can a creating_user job be patched by patching_user?
    """
    job = baker.make("jobs.Job", user=creating_user)
    new_status = models.Status.ERROR
    assert job.status is not new_status
    url = tp.reverse("apis:job-detail", pk=job.pk)

    # Can another user patch this job?
    tp.client.login(email=patching_user.email, password=password)
    payload = {"status": new_status}
    response = tp.client.patch(url, data=payload, content_type="application/json")
    assert response.status_code == http_status

    # Is Job.status correct, after patch attempt?
    job_obj = models.Job.objects.get(pk=job.pk)
    assert job_obj.status == exp_job_status


@pytest.mark.django_db()
def test_job_stats_url(tp, job):
    expected_url = "/apis/jobs/stats/"
    reversed_url = tp.reverse("apis:job-stats")
    assert expected_url == reversed_url


def test_job_stats_noauth(tp, job):
    """
    GET '/apis/jobs/stats/'
    """
    url = tp.reverse("apis:job-stats")

    # Without auth, API should return 401
    tp.get(url)
    tp.response_401()


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "test_user,expected",
    [
        (pytest.lazy_fixture("user"), 200),
        (pytest.lazy_fixture("staff"), 200),
        (pytest.lazy_fixture("superuser"), 200),
    ],
)
def test_job_stats(tp, job, password, test_user, expected):
    """
    GET '/apis/jobs/stats/'
    """
    url = tp.reverse("apis:job-stats")

    tp.client.login(email=test_user.email, password=password)

    response = tp.get(url)
    assert response.status_code == expected

    results = response.data["queued"]
    assert len(results) == 5
    assert results["active"] == models.Job.objects.exclude_imported().active().count()
    assert (
        results["complete"] == models.Job.objects.exclude_imported().complete().count()
    )
    assert results["deleted"] == models.Job.objects.exclude_imported().deleted().count()
    assert results["error"] == models.Job.objects.exclude_imported().error().count()
    assert results["queued"] == models.Job.objects.exclude_imported().queued().count()


def test_job_update_noauth(tp, job):
    """
    PUT '/apis/jobs/{pk}/'
    """
    url = tp.reverse("apis:job-detail", pk=job.pk)

    # Without auth, API should return 401
    tp.put(url)
    tp.response_401()


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "creating_user,updating_user,http_status, exp_job_status",
    [
        (pytest.lazy_fixture("user"), pytest.lazy_fixture("user"), 200, "error"),
        (pytest.lazy_fixture("user"), pytest.lazy_fixture("staff"), 200, "error"),
        (pytest.lazy_fixture("user"), pytest.lazy_fixture("superuser"), 200, "error"),
        (pytest.lazy_fixture("staff"), pytest.lazy_fixture("user"), 404, "queued"),
        (pytest.lazy_fixture("staff"), pytest.lazy_fixture("staff"), 200, "error"),
        (pytest.lazy_fixture("staff"), pytest.lazy_fixture("superuser"), 200, "error"),
        (pytest.lazy_fixture("superuser"), pytest.lazy_fixture("user"), 404, "queued"),
        (pytest.lazy_fixture("superuser"), pytest.lazy_fixture("staff"), 404, "queued"),
        (
            pytest.lazy_fixture("superuser"),
            pytest.lazy_fixture("superuser"),
            200,
            "error",
        ),
    ],
)
def test_job_update(
    tp, user, password, creating_user, updating_user, http_status, exp_job_status
):
    """
    PUT '/apis/jobs/{pk}/'
    Can a creating_user job be updated by updating_user?
    """
    job = baker.make("jobs.Job", user=creating_user)
    new_status = models.Status.ERROR
    assert job.status is not new_status

    url = tp.reverse("apis:job-detail", pk=job.pk)

    # Can another user update this job?
    tp.client.login(email=updating_user.email, password=password)
    payload = serializers.JobSerializer(instance=job).data
    payload["status"] = new_status
    response = tp.client.put(url, data=payload, content_type="application/json")
    assert response.status_code == http_status

    # Is Job.status correct, after update attempt?
    job_obj = models.Job.objects.get(pk=job.pk)
    assert job_obj.status == exp_job_status
