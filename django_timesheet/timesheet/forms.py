
from django.forms import ModelForm, ModelChoiceField, Select
from django.core import validators

from django_timesheet.timesheet.models import Task, File

class DatalistInput(Select):

    template_name = 'timesheet/forms/widgets/datalist_input.html'

class FileReferenceField(ModelChoiceField):

    widget = DatalistInput

    default_validators = [
        validators.MaxLengthValidator(File._meta.get_field('reference').max_length)
    ]

    def __init__(self, *args, **kwargs):
        kwargs.update(
            {
                'empty_label': None,
                'label': File._meta.get_field('reference').verbose_name,
            })
        return super().__init__(*args, **kwargs)

    def to_python(self, value):
        return value

    def prepare_value(self, obj):
        if hasattr(obj, 'reference'):
            return obj.reference
        return obj

    def label_from_instance(self, obj):
        return obj.reference

class TaskForm(ModelForm):

    field_order = ['reference', 'description']
    reference = FileReferenceField(required=False, queryset=File.objects.all())

    class Meta:
        model = Task
        fields = ['description']

    def save(self):
        task = super().save(commit=False)
        if self.cleaned_data['reference']:
            file, created = File.objects.get_or_create(reference=self.cleaned_data['reference'])
            task.file = file
        task.save()
        return task
