from django.contrib import admin

from . import models
from . import forms


class JobAdmin(admin.ModelAdmin):
    form = forms.JobAdminForm


admin.site.register(models.Job, JobAdmin)
@admin.register(models.JobLog)
class JobLogAdmin(admin.ModelAdmin):
    date_hierarchy = "created"
    list_display = ["job", "event", "created"]
    raw_id_fields = ["job"]
    search_fields = ["event"]
