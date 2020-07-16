from django.contrib import admin

# Register your models here.

from .models import User
from ftmap.models import Job


class JobRelationshipInline(admin.TabularInline):
    """ Make binds model accessible from another model's admin page """
    model = Job
    extra = 0

class UserAdmin(admin.ModelAdmin):
    inlines = (JobRelationshipInline,)

admin.site.register(User, UserAdmin)
