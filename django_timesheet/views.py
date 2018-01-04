
from django.views import generic

from django_timesheet.timesheet.models import Task

class HomePage(generic.TemplateView):

    template_name = 'django_timesheet/index.html'

    def get_context_data(self, **kwargs):
        qs = Task.objects.filter(timer__status__in=['running'])
        kwargs['object_list'] = qs
        return super().get_context_data(**kwargs)