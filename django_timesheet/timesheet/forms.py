
from django.forms import ModelForm, CharField, ModelChoiceField

from django_timesheet.timesheet.models import Task, File

class FileReferenceField(CharField):

    pass

class TaskForm(ModelForm):

    reference = FileReferenceField(required=False, max_length=128)

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
