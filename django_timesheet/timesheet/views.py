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

class TimerView(generic.DetailView):

    model = Task
    http_method_names = ['post']
    
    def post(self, request, pk):
        self.task = self.get_object()
        self.action()
        return redirect(self.task)

class StartTimer(TimerView):

    def action(self):
        self.task.start_timer()

class PauseTimer(TimerView):

    def action(self):
        self.task.timer.pause()

class ResumeTimer(TimerView):

    def action(self):
        self.task.timer.resume()

class StopTimer(TimerView):

    def action(self):
        self.task.timer.stop()

