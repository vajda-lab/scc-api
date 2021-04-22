"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import django_sql_dashboard

from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views
from sccApi.views import JobViewSet
from user_app.views import UserViewSet

router = DefaultRouter()
router.register("jobs", JobViewSet, basename="job")
router.register("users", UserViewSet, basename="user")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.HomeView.as_view(), name="home"),
    path("dashboard/", include(django_sql_dashboard.urls)),
    path("sccApi/", include(("sccApi.urls", "sccApi"), namespace="sccApi")),
    path("users/", include(("user_app.urls", "user_app"), namespace="user_app")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("apis/", include(router.urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)
