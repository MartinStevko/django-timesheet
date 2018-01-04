
from django.views import generic

class HomePage(generic.TemplateView):

    template_name = 'django_timesheet/index.html'