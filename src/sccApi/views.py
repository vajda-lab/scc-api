from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Job


class UserHomeView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "sccApi/user_home.html"

    def get_queryset(self):
        return self.model.objects.all()


class JobDetail(LoginRequiredMixin, DetailView):
    model = Job
    slug_field = "uuid"
    template_name = "sccApi/job_detail.html"