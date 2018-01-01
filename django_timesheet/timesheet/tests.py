from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.timezone import now

from django_timesheet.timesheet.models import File, Task

# Create your tests here.

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

    def test_timer_views(self):

        task = Task.objects.create()

        # Get not allowed
        response = self.client.get((reverse('start_timer', args=(task.pk,))))
        self.assertEqual(response.status_code, 405)

        # Start timer
        response = self.client.post(reverse('start_timer', args=(task.pk,)))

        self.assertRedirects(response, task.get_absolute_url())
        task.refresh_from_db()
        timer = task.timer
        self.assertTrue(timer.running)

        # Pause timer
        response = self.client.post(reverse('pause_timer', args=(task.pk,)))
        self.assertTrue(timer.paused)

        # Resume timer
        response = self.client.post(reverse('resume_timer', args=(task.pk,)))
        self.assertTrue(timer.running)

        # Stop timer
        response = self.client.post(reverse('stop_timer', args=(task.pk,)))
        timer.refresh_from_db()
        self.assertTrue(timer.stopped)
        