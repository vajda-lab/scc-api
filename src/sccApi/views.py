from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets

from .models import Job
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

    # def list(self, request):
    #     pass

    def create(self, request):
        response = super().create(request)
        tasks.create_job.delay(self.get_object().pk)
        return response

    # def retrieve(self, request, pk=None):
    #     pass

    def update(self, request, pk=None, **kwargs):
        response = super().update(request, pk=pk, **kwargs)
        tasks.update_job_priority.delay(pk)
        return response

    def partial_update(self, request, pk=None):
        response = super().partial_update(request, pk=pk)
        tasks.update_job_priority.delay(pk)
        return response

    def destroy(self, request, pk=None):
        tasks.delete_job.delay(pk)
        response = super().destroy(request, pk=pk)
        return response
