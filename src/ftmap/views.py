from django.views.generic import ListView, CreateView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Job
from .forms import JobSubmitform
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect



class UserHomeView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "ftplus/user_home.html"

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class JobEditMixin(object):
    """
    Common helper for job create/edit.

    Provides:
        * success messages
        * redirect to the user homepage on success
    """

    form_class = JobSubmitform
    model = Job

    def get_context_data(self, **kwargs):
        context = super(JobEditMixin, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, self.success_message)
        return super(JobEditMixin, self).form_valid(form)

    def get_success_url(self):
        return reverse("ftmap:user_home")


class JobCreate(LoginRequiredMixin, JobEditMixin, CreateView):
    """
    Create a new job.
    """

    template_name = "ftplus/job_create.html"

    # our custom fields
    navitem = "new"

    success_message = "Your job has been submitted."

    def get_form_kwargs(self):
        kwargs = super(JobCreate, self).get_form_kwargs()
        kwargs["instance"] = Job(
            user=self.request.user
        )
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.clean()
        return super().form_valid(form)


class ChangeJobStatus(object):
    """
    Abstract class to change a job's status; see the concrete implentations below.
    """

    def post(self, request, uuid):
        job = get_object_or_404(request.user.job, uuid=uuid)
        job.status = self.new_status
        job.save()
        messages.add_message(self.request, messages.SUCCESS, self.success_message)
        return redirect("ftmap:user_home")

class DeleteJob(LoginRequiredMixin, ChangeJobStatus, View):
    new_status = Job.STATUS_DELETED
    success_message = "Your job has been deleted."


class JobDetail(LoginRequiredMixin, DetailView):
    model = Job
    slug_field = "uuid"
    template_name = "ftplus/job_detail.html"