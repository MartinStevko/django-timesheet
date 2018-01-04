from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.db import IntegrityError

from django_timesheet.timesheet.models import File, Task

# Create your tests here.

class TimesheetModels(TestCase):

    def test_task_with_timer(self):
        task = Task.objects.create()
        task.timer.start()
        self.assertEqual(task.timer.status, 'running')

    def test_file_reference_unique(self):
        File.objects.create(reference='abc')
        with self.assertRaises(IntegrityError):
            File.objects.create(reference='abc')

class TimesheetViews(TestCase):

    def test_create_file(self):

        response = self.client.get(reverse('create_file'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('create_file'),
            data={'reference': 'foo'})


        file = File.objects.first()
        self.assertEqual(file.reference, 'foo')
        self.assertEqual(File.objects.count(), 1)

        self.assertRedirects(response, file.get_absolute_url())

    def test_create_task(self):

        file = File.objects.create(reference='foo')

        response = self.client.get(reverse('create_task'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('create_task'),
            data={
                'file': file.pk,
                'description': 'foo'
            })

        task = Task.objects.first()
        self.assertEqual(task.description, 'foo')
        self.assertEqual(task.date, now().date())
        self.assertEqual(Task.objects.count(), 1)

        self.assertRedirects(response, task.get_absolute_url())

        # Create task without file
        response = self.client.post(reverse('create_task'),
            data={'description': 'bar'})

        task = Task.objects.get(description='bar')
        self.assertIsNone(task.file)

    def test_create_task_from_file(self):

        file = File.objects.create()

        response = self.client.get(reverse('create_task', args=(file.pk,)))
        self.assertEqual(response.context['form'].initial['file'], file.pk)

    def test_timer_views(self):

        task = Task.objects.create()
        timer = task.timer

        # Start timer
        response = self.client.post(reverse('start_timer', args=(timer.pk,)))
        timer.refresh_from_db()
        self.assertTrue(timer.status, 'running')

        # Pause timer
        response = self.client.post(reverse('pause_timer', args=(timer.pk,)))
        timer.refresh_from_db()
        self.assertTrue(timer.status, 'paused')

        # Resume timer
        response = self.client.post(reverse('resume_timer', args=(timer.pk,)))
        timer.refresh_from_db()
        self.assertTrue(timer.status, 'running')

        # Stop timer
        response = self.client.post(reverse('stop_timer', args=(timer.pk,)))
        timer.refresh_from_db()
        self.assertTrue(timer.status, 'stopped')

    def test_files_list(self):

        File.objects.create(reference='a123')
        File.objects.create(reference='b123')
        File.objects.create(reference='c123')

        response = self.client.get(reverse('file_list'))
        self.assertEqual(response.context['object_list'].count(), 3)

        # Search list
        response = self.client.get(reverse('file_list'), data={'reference': 'b'})
        self.assertEqual(response.context['object_list'].count(), 1)
                
    def test_home_page(self):

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'timesheet/index.html')