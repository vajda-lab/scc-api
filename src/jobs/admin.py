from django.contrib import admin

from . import forms
from . import models


class JobLogInline(admin.TabularInline):
    model = models.JobLog


@admin.register(models.Job)
class JobAdmin(admin.ModelAdmin):
    form = forms.JobAdminForm
    inlines = [
        JobLogInline,
    ]
    list_display = [
        "uuid",
        "imported",
        "sge_task_id",
        "status",
        "priority",
        "job_ja_task_id",
        "input_file",
        "output_file",
        "created",
        "modified",
    ]
    list_filter = [
        "status",
        "priority",
        "imported",
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
