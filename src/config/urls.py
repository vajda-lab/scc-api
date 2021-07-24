import django_sql_dashboard

from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import __version__
from . import views
from jobs.views import JobViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register("jobs", JobViewSet, basename="job")
router.register("users", UserViewSet, basename="user")

admin_header = f"Vajda Lab SCC API v{__version__}"
admin.site.enable_nav_sidebar = False
admin.site.site_header = admin_header
admin.site.site_title = admin_header

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.HomeView.as_view(), name="home"),
    path("dashboard/", include(django_sql_dashboard.urls)),
    path("jobs/", include(("jobs.urls", "jobs"), namespace="jobs")),
    path("users/", include(("users.urls", "users"), namespace="users")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("apis/", include(router.urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)
