from django.urls import path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"jobs", views.JobViewSet, basename="job")

app_name = 'sccApi'
urlpatterns = [
    path('', views.UserHomeView.as_view(), name="user_home"),
    path("<slug>/", views.JobDetail.as_view(), name="job_detail"),
]

urlpatterns += router.urls
