from django.shortcuts import redirect
from django.views import generic

from django_timesheet.timesheet.models import File, Task


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

class StartTimer(generic.DetailView):

    model = Task
    http_method_names = ['post']
    
    def post(self, request, pk):
        task = self.get_object()
        task.start_timer()
        return redirect(task)
