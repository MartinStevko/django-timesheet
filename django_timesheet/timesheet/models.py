from django.db import models
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import gettext_lazy as _

from django_timer.models import Timer

# Create your models here.

class File(models.Model):

    reference = models.CharField(_('Aktenzeichen'), max_length=128)

    def get_absolute_url(self):
        return reverse_lazy('file', args=(self.pk,))

class Task(models.Model):

    file = models.ForeignKey(to=File, verbose_name=_('Akte'), blank=True, null=True)
    date = models.DateField(_('Datum'), auto_now_add=True)
    description = models.TextField(_('Beschreibung'))
    timer = models.OneToOneField(to=Timer, null=True)

    def get_absolute_url(self):
        return reverse_lazy('task', args=(self.pk,))

    def start_timer(self):
        if not self.timer:
            self.timer = Timer.objects.start()
            self.save()
