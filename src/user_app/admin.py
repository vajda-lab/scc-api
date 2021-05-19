from django.contrib import admin

from .models import User
from jobs.models import Job


class JobRelationshipInline(admin.TabularInline):
    """Make binds model accessible from another model's admin page"""

    model = Job
    extra = 0


class UserAdmin(admin.ModelAdmin):
    inlines = (JobRelationshipInline,)


admin.site.register(User, UserAdmin)
