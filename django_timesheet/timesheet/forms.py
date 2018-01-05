
from django.forms import Form, CharField, TextInput, ChoiceField, ModelChoiceField
from django.core import validators

from django_timesheet.timesheet.models import Task, File

class DatalistInput(TextInput):

    template_name = 'timesheet/forms/widgets/datalist_input.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['datalist'] = list(self.choices)
        return context

class DataListIterator(object):

    def __init__(self, field):
        self.field = field
        self.queryset = self.field.queryset

    def __iter__(self):
        for obj in self.queryset.all().iterator():
            yield (obj.reference, obj.reference)

class FileReferenceField(CharField):

    widget = DatalistInput
    iterator = DataListIterator

    def __init__(self, queryset, *args, **kwargs):
        self.queryset = queryset
        return super().__init__(*args, **kwargs)

    def _get_queryset(self):
        return self._queryset

    def _set_queryset(self, queryset):
        self._queryset = queryset
        self.widget.choices = self.choices

    queryset = property(_get_queryset, _set_queryset)

    def _get_choices(self):
        return self.iterator(self)

    choices = property(_get_choices, ChoiceField._set_choices)

class TaskForm(Form):

    field_order = ['reference', 'description']
    
    reference = FileReferenceField(
        required=False, 
        queryset=File.objects.all(),
        max_length=File._meta.get_field('reference').max_length, 
        label=File._meta.get_field('reference').verbose_name
    )

    description = Task._meta.get_field('description').formfield()

    def save(self):
        task = Task(description=self.cleaned_data['description'])
        if self.cleaned_data['reference']:
            file, created = File.objects.get_or_create(reference=self.cleaned_data['reference'])
            task.file = file
        task.save()
        return task
