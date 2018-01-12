from django.conf.urls import url

from django_timesheet.timesheet import views
from django.views import generic

from django_timesheet.timesheet.models import File, Task

urlpatterns = [
    url(r'^$',
        views.HomePage.as_view(),
        name='index'),
    url(r'^file/$',
        views.FileListView.as_view(),
        name='file_list'),
    url(r'^file/(?P<pk>\d+)/$',
        generic.UpdateView.as_view(model=File, fields=['reference']),
        name='file'),
    url(r'^file/(?P<pk>\d+)/task/create/$',
        views.TaskCreateView.as_view(),
        name='create_task'),
    url(r'^task/(?P<pk>\d+)/$',
        generic.UpdateView.as_view(model=Task, fields=['description', 'billable', 'min_billable_time']),
        name='task'),
    url(r'^task/(?P<pk>\d+)/set_billable_time/$',
        views.TaskSetBillableTimeView.as_view(),
        name='set_billable_time'),
    url(r'^task/archive/$',
        views.TaskArchive.as_view(),
        name='task_archive'),
    url(r'^task/archive/(?P<year>\d{4})/$',
        views.TaskYearArchive.as_view(),
        name='task_archive'),
    url(r'^task/archive/(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        views.TaskMonthArchive.as_view(),
        name='task_archive'),
    url(r'^task/archive/(?P<year>\d{4})/(?P<month>\d{1,2})/pdf/$',
        views.MonthlyTaskPDFView.as_view(),
        name='task_archive_pdf'),
]