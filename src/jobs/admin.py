from django.contrib import admin

from . import forms
from . import models


@admin.register(models.Job)
class JobAdmin(admin.ModelAdmin):
    form = forms.JobAdminForm
    list_display = [
        "user",
        "input_file",
        "output_file",
        "status",
        "priority",
        "uuid",
        "sge_task_id",
        "job_ja_task_id",
    ]
    list_filter = [
        "status",
        "priority",
    ]
    raw_id_fields = ["user"]
    readonly_fields = ["created", "modified"]
    search_fields = ["uuid", "sge_task_id"]


@admin.register(models.JobLog)
class JobLogAdmin(admin.ModelAdmin):
    date_hierarchy = "created"
    list_display = ["job", "event", "created"]
    raw_id_fields = ["job"]
    search_fields = ["event"]
