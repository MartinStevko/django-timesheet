from django.conf.urls import url

from django_timesheet.timesheet import views

urlpatterns = [
    url(r'^$', views.HomePage.as_view(), name='index'),
    url(r'^file/$', views.FileListView.as_view(), name='file_list'),
    url(r'^file/create/$', views.FileCreateView.as_view(), name='create_file'),
    url(r'^file/(?P<pk>\d+)/$', views.FileUpdateView.as_view(), name='file'),
    url(r'^file/(?P<pk>\d+)/task/create/$', views.TaskCreateView.as_view(), name='create_task'),
    url(r'^task/create/$', views.TaskCreateView.as_view(), name='create_task'),
    url(r'^task/(?P<pk>\d+)/$', views.TaskUpdateView.as_view(), name='task'),
]