
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic

from django_tex.views import render_to_pdf

from django_timesheet.timesheet.models import File, Task
from django_timesheet.timesheet.forms import TaskForm, FileSearchForm
from django_timesheet.timesheet.filters import TaskFilter, FileFilter

class FilterMixin(object):

    def get_context_data(self, **kwargs):
        f = self.filter(self.request.GET, self.object_list)
        kwargs['f'] = f
        kwargs.update({'object_list': f.qs})
        return super().get_context_data(**kwargs)

class HomePage(generic.TemplateView):

    template_name = 'timesheet/index.html'

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = TaskForm()
        if 'search_form' not in kwargs:
            kwargs['search_form'] = FileSearchForm()
        kwargs['object_list'] = Task.objects.filter(timer__status__in=['', 'running', 'paused'])
        return super().get_context_data(**kwargs)

    def post(self, request):
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('index'))
        return self.render_to_response(self.get_context_data(form=form))

class FileListView(FilterMixin, generic.ListView):

    model = File
    filter = FileFilter

    def render_to_response(self, context):
        if context['object_list'].count() == 1:
            return redirect(context['object_list'].first())
        return super().render_to_response(context)

class FileUpdateView(generic.UpdateView):

    model = File
    fields = ('reference',)

class TaskListView(FilterMixin, generic.ListView):

    model = Task
    filter = TaskFilter

class TaskCreateView(generic.CreateView):

    model = Task
    fields = ('file', 'description')

    def get_initial(self):
        if 'pk' in self.kwargs:
            self.file = get_object_or_404(File, pk=self.kwargs['pk'])
            return {'file': self.file.pk}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'file'):
            context['file'] = self.file
        return context

class TaskUpdateView(generic.UpdateView):

    model = Task
    fields = ('description', 'billable', 'min_billable_time')

class TaskSetBillableTimeView(generic.DetailView):

    model = Task
    http_method_names= ['post']

    def post(self, request, **kwargs):
        task = self.get_object()
        task.to_billable_time()
        return redirect(task)

class TaskPdfListView(TaskListView):

    template_name = 'timesheet/task_list.tex'

    def render_to_response(self, context, **response_kwargs):
        return render_to_pdf(self.template_name, context)

class MonthlyTaskPDFView(generic.dates.MonthArchiveView):

    model = Task
    date_field = 'date'
    template_name = 'timesheet/task_list.tex'

    def render_to_response(self, context, **response_kwargs):
        return render_to_pdf(self.template_name, context)

