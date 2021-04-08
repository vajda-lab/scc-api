from django.conf.urls import url
from . import views
app_name = 'user_app'
urlpatterns = [
    url('', views.signup, name='signup'),
]