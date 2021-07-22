from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone
from django.views.generic import ListView, DetailView
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from . import serializers
from . import tasks
from .models import Job, JobLog, Status


class JobDetail(LoginRequiredMixin, DetailView):
    model = Job
    slug_field = "uuid"
    template_name = "jobs/job_detail.html"


class UserHomeView(LoginRequiredMixin, ListView):
    paginate_by = 100
    template_name = "jobs/user_home.html"

    def get_queryset(self):
        return self.model.objects.exclude_imported().filter(
            created=timezone.now() - timedelta(days=7),
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
            return Job.objects.all().exclude(imported=True)

        # Staff have access to all Jobs except for Superuser Jobs
        if self.request.user.is_staff:
            if self.action in ["list", "retrieve"]:
                return Job.objects.all().exclude(imported=True)
            return Job.objects.filter(user__is_superuser=False).exclude(imported=True)

        # Everyone else can only access their own Jobs
        return Job.objects.filter(user=self.request.user).exclude(imported=True)

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
