from django.urls import path

from . import views

app_name = "jobs"
urlpatterns = [
    path("", views.UserHomeView.as_view(), name="user_home"),
    path("<slug>/", views.JobDetail.as_view(), name="job_detail"),
]
