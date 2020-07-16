from django.urls import path

from . import views
app_name = 'ftmap'
urlpatterns = [
    path('', views.UserHomeView.as_view(), name="user_home"),
    path("create/", views.JobCreate.as_view(), name="job_create"),
    path("<slug>/", views.JobDetail.as_view(), name="job_detail"),
]