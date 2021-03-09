from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets

from .models import Job
from . import serializers


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

        if self.request.user.is_superuser:
            return Job.objects.all()

        if self.action in ["list", "retrieve"]:
            return Job.objects.all()
        else:
            if self.request.user.is_staff:
                return Job.objects.all()
            return Job.objects.filter(user=self.request.user)
