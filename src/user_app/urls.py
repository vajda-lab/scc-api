from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")

app_name = 'user_app'
urlpatterns = [
    url('', views.signup, name='signup'),
]

urlpatterns += router.urls
