
from math import ceil
from datetime import timedelta

from django.db import models
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

from django_timer.models import Timer

# Create your models here.

class File(models.Model):

    reference = models.CharField(_('Aktenzeichen'), max_length=128, unique=True)

    def get_absolute_url(self):
        return reverse_lazy('file', args=(self.pk,))

    def __str__(self):
        return self.reference

class TaskQueryset(models.QuerySet):

    def total_billable_time(self):
        return self.aggregate(models.Sum('billable'))['billable__sum']

    def pending(self):
        return self.filter(timer__status__in=['', 'running', 'paused'])

    def today(self):
        return self.filter(date=now().date())

class Task(models.Model):

    file = models.ForeignKey(to=File, verbose_name=_('Akte'), blank=True, null=True)
    date = models.DateField(_('Datum'), auto_now_add=True)
    description = models.TextField(_('Beschreibung'))
    timer = models.OneToOneField(to=Timer, null=True)
    billable = models.DurationField(_('Abrechenbare Zeit'), null=True, blank=True)
    min_billable_time = models.DurationField(_('kleinste Zeiteinheit'), default=timedelta(seconds=15*60))

    objects = TaskQueryset.as_manager()

    def get_absolute_url(self):
        return reverse_lazy('task', args=(self.pk,))

    def start_timer(self):
        if not self.timer:
            self.timer = Timer.objects.start()
            self.save()

    def save(self, *args, **kwargs):
        if not self.timer:
            self.timer = Timer.objects.create()
        return super().save(*args, **kwargs)

    def to_billable_time(self):
        duration = ceil(self.timer.duration()/self.min_billable_time)*self.min_billable_time
        self.billable = duration
        self.save()