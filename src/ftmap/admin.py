from django.contrib import admin

from . import models
from . import forms

class JobAdmin(admin.ModelAdmin):
    form = forms.JobAdminForm

admin.site.register(models.Job, JobAdmin)


class JobPageAdmin(admin.ModelAdmin):
    admin.site.register(models.Example)
