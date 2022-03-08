from datetime import timedelta
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone
from django.views.generic import DetailView, ListView
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import serializers
from . import tasks
from .models import Job, JobLog, Status


class JobDetail(LoginRequiredMixin, DetailView):
    model = Job
    slug_field = "uuid"
    template_name = "jobs/job_detail.html"


class JobList(LoginRequiredMixin, ListView):
    model = Job
    paginate_by = 100
    template_name = "jobs/job_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "job_active_count": Job.objects.exclude_imported().active().count(),
                "job_complete_count": Job.objects.exclude_imported().complete().count(),
                "job_deleted_count": Job.objects.exclude_imported().deleted().count(),
                "job_error_count": Job.objects.exclude_imported().error().count(),
                "job_queued_count": Job.objects.exclude_imported().queued().count(),
            }
        )
        return context

    def get_queryset(self):
        return self.model.objects.exclude_imported().filter(
            created__gt=timezone.now() - timedelta(days=7),
            status__in=[
                Status.ACTIVE,
                Status.COMPLETE,
                Status.ERROR,
                Status.QUEUED,
            ],
        )


class JobViewSet(viewsets.ModelViewSet):
    """A viewset for viewing and editing Job instances."""

    serializer_class = serializers.JobSerializer
    ordering = "created"
    filterset_fields = [
        "imported",
        "sge_task_id",
        "status",
        "user",
    ]

    def get_queryset(self):
        """
        View should return a list of jobs.
        created by the currently authenticated user.
        """

        # Superusers have access to all Jobs
        if self.request.user.is_superuser:
            return Job.objects.exclude_imported()

        # Staff have access to all Jobs except for Superuser Jobs
        if self.request.user.is_staff:
            if self.action in ["list", "retrieve"]:
                return Job.objects.exclude_imported()
            return Job.objects.filter(user__is_superuser=False).exclude_imported()

        # Everyone else can only access their own Jobs
        return Job.objects.filter(user=self.request.user).exclude_imported()

    def create(self, request):
        """
        Add a new Job instance to the task queue.

        POST '/apis/jobs/'
        """

        # Collect the user making the request and pass into our serializer.
        request.data["user"] = request.user.pk

        # Proxy the request to create a new Job.
        response = super().create(request)

        return response

    def destroy(self, request, pk=None):
        """
        Delete a Job.

        DELETE '/apis/jobs/{pk}/'

        Deletes should be "soft" deleted where we mark the Job's status
        as `DELETED` instead of removing the job.
        """
        instance = self.get_object()
        instance.status = Status.DELETED
        instance.save()

        JobLog.objects.create(job=instance, event="Job status changed to deleted")

        # Call Celery to manage our job.
        tasks.delete_job.delay(pk=pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk=None):
        """
        Change the priority of a Job.

        PATCH '/apis/jobs/{pk}/'
        """

        # Proxy the request to partial update the Job.
        response = super().partial_update(request, pk=pk)

        instance = self.get_object()
        with transaction.atomic():
            # Call Celery update the priority of the job.
            tasks.update_job_priority.delay(pk=pk, new_priority=instance.priority)

        return response

    @action(detail=False)
    def stats(self, request):
        """
        GET '/apis/jobs/stats/'
        """
        data = {
            "queued": {
                "active": Job.objects.exclude_imported().active().count(),
                "complete": Job.objects.exclude_imported().complete().count(),
                "deleted": Job.objects.exclude_imported().deleted().count(),
                "error": Job.objects.exclude_imported().error().count(),
                "queued": Job.objects.exclude_imported().queued().count(),
            },
            "queued-with-imported": {
                "active": Job.objects.active().count(),
                "complete": Job.objects.complete().count(),
                "deleted": Job.objects.deleted().count(),
                "error": Job.objects.error().count(),
                "queued": Job.objects.queued().count(),
            },
            "settings": {
                "SCC_MAX_HIGH_JOBS": settings.SCC_MAX_HIGH_JOBS,
                "SCC_MAX_LOW_JOBS": settings.SCC_MAX_LOW_JOBS,
                "SCC_MAX_NORMAL_JOBS": settings.SCC_MAX_NORMAL_JOBS,
            },
        }
        return Response(data)

    def update(self, request, pk=None, **kwargs):
        """
        Update a Job

        PUT '/apis/jobs/{pk}/'
        """

        # Proxy the request to update the Job.
        response = super().update(request, pk=pk, **kwargs)

        instance = self.get_object()
        with transaction.atomic():
            # Call Celery update the priority of the job.
            tasks.update_job_priority.delay(pk=pk, new_priority=instance.priority)

        return response
