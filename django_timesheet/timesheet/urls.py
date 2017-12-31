from django.conf.urls import url

from django_timesheet.timesheet import views

urlpatterns = [
    url(r'^file/create/$', views.FileCreateView.as_view(), name='create_file'),
    url(r'^file/(?P<pk>\d+)/$', views.FileUpdateView.as_view(), name='file'),
    url(r'^task/create/$', views.TaskCreateView.as_view(), name='create_task'),
    url(r'^task/(?P<pk>\d+)/$', views.TaskUpdateView.as_view(), name='task'),
]