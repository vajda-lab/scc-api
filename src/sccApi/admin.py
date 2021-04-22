from django.contrib import admin

from . import forms
from . import models


@admin.register(models.Job)
class JobAdmin(admin.ModelAdmin):
    form = forms.JobAdminForm
    raw_id_fields = ["user"]


@admin.register(models.JobLog)
class JobLogAdmin(admin.ModelAdmin):
    date_hierarchy = "created"
    list_display = ["job", "event", "created"]
    raw_id_fields = ["job"]
    search_fields = ["event"]
