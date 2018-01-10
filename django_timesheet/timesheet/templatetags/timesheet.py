
from django.template import Library

register = Library()

@register.inclusion_tag('timesheet/includes/form.html')
def render_form(form):
    return {'form': form}
