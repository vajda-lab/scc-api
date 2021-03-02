from django.forms import ModelForm

from .models import Job


class JobSubmitform(ModelForm):
    class Meta(object):
        model = Job
        fields = "__all__"


class JobAdminForm(ModelForm):
    class Meta:
        model = Job
        fields = "__all__"
