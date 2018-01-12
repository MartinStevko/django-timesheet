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
    url(r'^task/$',
        views.TaskListView.as_view(),
        name='task_list'),
    url(r'^task/pdf/$',
        views.TaskPdfListView.as_view(),
        name='task_list_pdf'),
    url(r'^task/(?P<pk>\d+)/$',
        generic.UpdateView.as_view(model=Task, fields=['description', 'billable', 'min_billable_time']),
        name='task'),
    url(r'^task/(?P<pk>\d+)/set_billable_time/$',
        views.TaskSetBillableTimeView.as_view(),
        name='set_billable_time'),
    url(r'^task/archive/$',
        generic.dates.ArchiveIndexView.as_view(model=Task, date_field='date'),
        name='task_archive'),
    url(r'^task/archive/(?P<year>\d{4})/$',
        generic.dates.YearArchiveView.as_view(model=Task, date_field='date'),
        name='task_archive'),
    url(r'^task/archive/(?P<year>\d{4})/(?P<month>\w+)/$',
        generic.dates.MonthArchiveView.as_view(model=Task, date_field='date'),
        name='task_archive'),
    url(r'^task/archive/(?P<year>\d{4})/(?P<month>\w+)/pdf/$',
        views.MonthlyTaskPDFView.as_view(),
        name='task_archive_pdf'),
]