from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.views.generic import ListView, DetailView
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Job, JobLog
from . import serializers
from . import tasks


class UserHomeView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "sccApi/user_home.html"

    def get_queryset(self):
        return self.model.objects.all()


class JobDetail(LoginRequiredMixin, DetailView):
    model = Job
    slug_field = "uuid"
    template_name = "sccApi/job_detail.html"


class JobViewSet(viewsets.ModelViewSet):
    """A viewset for viewing and editing Job instances."""

    serializer_class = serializers.JobSerializer
    ordering = "created"

    def get_queryset(self):
        """
        View should return a list of jobs.
        created by the currently authenticated user.
        """

        # Superusers have access to all Jobs
        if self.request.user.is_superuser:
            return Job.objects.all()

        # Staff have access to all Jobs except for Superuser Jobs
        if self.request.user.is_staff:
            if self.action in ["list", "retrieve"]:
                return Job.objects.all()
            return Job.objects.filter(user__is_superuser=False)

        # Everyone else can only access their own Jobs
        return Job.objects.filter(user=self.request.user)

    def create(self, request):
        """
        Add a new Job instance to the task queue.
        """
        request.data["user"] = request.user.pk
        response = super().create(request)
        # pk = response.data.get("uuid")
        # tasks.create_job.delay(pk=pk)
        return response

    def destroy(self, request, pk=None):
        """
        Delete a Job.
        """
        instance = self.get_object()
        instance.status = Job.STATUS_DELETED
        instance.save()

        JobLog.objects.create(job=instance, event="Job status changed to deleted")

        # Call Celery to manage our job.
        tasks.delete_job.delay(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk=None, new_priority=None):
        """
        Change the priority of a Job.
        """
        response = super().partial_update(request, pk=pk)
        with transaction.atomic():
            # Call Celery update the priority of the job.
            tasks.update_job_priority.delay(pk, new_priority)
        return response

    def update(self, request, pk=None, new_priority=None, **kwargs):
        """
        Update a Job
        """
        response = super().update(request, pk=pk, **kwargs)
        with transaction.atomic():
            # Call Celery update the priority of the job.
            tasks.update_job_priority.delay(pk, new_priority)
        return response
