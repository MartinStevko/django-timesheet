from django.conf.urls import url

from django_timesheet.timesheet import views

urlpatterns = [
    url(r'^file/$', views.FileListView.as_view(), name='file_list'),
    url(r'^file/create/$', views.FileCreateView.as_view(), name='create_file'),
    url(r'^file/(?P<pk>\d+)/$', views.FileUpdateView.as_view(), name='file'),
    url(r'^task/create/$', views.TaskCreateView.as_view(), name='create_task'),
    url(r'^task/(?P<pk>\d+)/$', views.TaskUpdateView.as_view(), name='task'),
    url(r'^task/(?P<pk>\d+)/start_timer/$', views.StartTimer.as_view(), name='start_timer'),
    url(r'^task/(?P<pk>\d+)/pause_timer/$', views.PauseTimer.as_view(), name='pause_timer'),
    url(r'^task/(?P<pk>\d+)/resume_timer/$', views.ResumeTimer.as_view(), name='resume_timer'),
    url(r'^task/(?P<pk>\d+)/stop_timer/$', views.StopTimer.as_view(), name='stop_timer'),
]