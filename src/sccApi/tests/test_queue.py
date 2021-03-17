import pytest

from model_bakery import baker

from sccApi import models, serializers
from user_app.models import User


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
def test_task_delete(
    tp, password, creating_user, deleting_user, http_status, expected_jobs
):
    """
    DELETE '/apis/jobs/{pk}/'
    Can a creating_user task be deleted by deleting_user?
    """
    job = baker.make("sccApi.Job", user=creating_user)
    url = tp.reverse("job-destroy", pk=job.pk)

    # Can another user delete this job?
    tp.client.login(email=deleting_user.email, password=password)
    response = tp.client.delete(url, content_type="application/json")
    assert response.status_code == http_status

    # Do we have the correct number of jobs, after delete attempt
    assert models.Job.objects.filter(pk=job.pk).count() == expected_jobs

