from django.conf.urls import url


from . import views

app_name = 'user_app'
urlpatterns = [
    url('signup/', views.signup, name='signup'),
    url('', views.UserListView.as_view(), name='list-user'),
]
