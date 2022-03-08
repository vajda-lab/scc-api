from django.urls import path

from . import views

app_name = "jobs"
urlpatterns = [
    path("", views.JobList.as_view(), name="user_home"),
    path("<slug>/", views.JobDetail.as_view(), name="job_detail"),
]
