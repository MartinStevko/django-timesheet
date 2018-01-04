from django.shortcuts import redirect
from django.views import generic

from django_timesheet.timesheet.models import File, Task

class FileListView(generic.ListView):

    model = File

    def get_queryset(self):
        queryset = super().get_queryset()
        lookup = self.request.GET.get('reference', None)
        if lookup:
            queryset = queryset.filter(reference__icontains=lookup)
        return queryset

class FileCreateView(generic.CreateView):

    model = File
    fields = ('reference',)

class FileUpdateView(generic.UpdateView):

    model = File
    fields = ('reference',)

class TaskCreateView(generic.CreateView):

    model = Task
    fields = ('file', 'description')

class TaskUpdateView(generic.UpdateView):

    model = Task
    fields = ('description',)
