
from django.forms import Form, CharField, TextInput, ChoiceField, ModelForm, HiddenInput, Textarea
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

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
            yield (self.field.prepare_value(obj), self.field.label_from_instance(obj))

class DataListCharField(CharField):

    widget = DatalistInput(attrs={'class': 'autocomplete'})
    iterator = DataListIterator

    def __init__(self, queryset, to_field_name=None, *args, **kwargs):
        self.to_field_name = to_field_name
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

    def prepare_value(self, value):
        if self.to_field_name and hasattr(value, self.to_field_name):
            return getattr(value, self.to_field_name)
        return super().prepare_value(value)

    def label_from_instance(self, obj):
        if self.to_field_name and hasattr(obj, self.to_field_name):
            return getattr(obj, self.to_field_name)
        return str(obj)

class TaskFromFileForm(ModelForm):

    class Meta:
        model = Task
        fields = ['file', 'description']
        widgets = {
            'file': HiddenInput,
        }

class TaskForm(Form):

    field_order = ['reference', 'description']
    
    reference = DataListCharField(
        required=False, 
        to_field_name='reference',
        queryset=File.objects.all(),
        max_length=File._meta.get_field('reference').max_length, 
        label=File._meta.get_field('reference').verbose_name
    )

    description = CharField(required=False)

    def clean_description(self):
        data = self.cleaned_data['description']
        if not data:
            raise ValidationError(_('This field is required.'), code='required')
        return data

    def save(self):
        task = Task(description=self.cleaned_data['description'])
        if self.cleaned_data['reference']:
            file, created = File.objects.get_or_create(reference=self.cleaned_data['reference'])
            task.file = file
        task.save()
        return task

class FileSearchForm(Form):

    reference = DataListCharField(
        required=False, 
        to_field_name='reference',
        queryset=File.objects.all(),
        label='Suchen'
    )