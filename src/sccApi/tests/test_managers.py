import pytest

from model_bakery import baker

from ..models import Job, Priority, Status


@pytest.mark.django_db()
def test_job_manager_priority_high():
    baker.make("sccApi.Job", priority=Priority.HIGH)
    assert Job.objects.high_priority().count() == 1


@pytest.mark.django_db()
def test_job_manager_priority_low():
    baker.make("sccApi.Job", priority=Priority.LOW)
    assert Job.objects.low_priority().count() == 1


@pytest.mark.django_db()
def test_job_manager_priority_normal():
    baker.make("sccApi.Job", priority=Priority.NORMAL)
    assert Job.objects.normal_priority().count() == 1


@pytest.mark.django_db()
def test_job_manager_status_active():
    baker.make("sccApi.Job", status=Status.ACTIVE)
    assert Job.objects.active().count() == 1


@pytest.mark.django_db()
def test_job_manager_status_complete():
    baker.make("sccApi.Job", status=Status.COMPLETE)
    assert Job.objects.complete().count() == 1


@pytest.mark.django_db()
def test_job_manager_status_deleted():
    baker.make("sccApi.Job", status=Status.DELETED)
    assert Job.objects.deleted().count() == 1


@pytest.mark.django_db()
def test_job_manager_status_error():
    baker.make("sccApi.Job", status=Status.ERROR)
    assert Job.objects.error().count() == 1


@pytest.mark.django_db()
def test_job_manager_status_queued():
    baker.make("sccApi.Job", status=Status.QUEUED)
    assert Job.objects.queued().count() == 1
