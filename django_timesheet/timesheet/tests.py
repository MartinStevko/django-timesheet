
import datetime
from time import sleep

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.utils.timezone import now

from django_timesheet.timesheet.models import File, Task
from django_timesheet.timesheet.forms import TaskForm

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

    def test_timer_to_billable_hours(self):
        task = Task.objects.create()
        start = now()
        task.timer.segment_set.create(
            start_time = start,
            stop_time = start + datetime.timedelta(seconds=15*60)
        )
        self.assertAlmostEqual(task.timer.duration().total_seconds(), 15*60, delta=0.01)
        task.to_billable_time()
        self.assertAlmostEqual(task.billable.total_seconds(), 15*60, delta=0.01)

    def test_timer_to_billable_hours_with_min_duration_unit(self):
        task = Task.objects.create(min_billable_time=datetime.timedelta(seconds=15*60))
        start = now()
        task.timer.segment_set.create(
            start_time = start,
            stop_time = start + datetime.timedelta(seconds=20*60)
        )
        self.assertAlmostEqual(task.timer.duration().total_seconds(), 20*60, delta=0.01)
        task.to_billable_time()
        self.assertAlmostEqual(task.billable.total_seconds(), 30*60, delta=0.01)

    def test_total_billable_time(self):

        f = File.objects.create()
        Task.objects.create()
        Task.objects.create(file=f, description='a', billable=datetime.timedelta(seconds=15*60))
        Task.objects.create(description='a', billable=datetime.timedelta(seconds=15*60))
        Task.objects.create(file=f, description='b', billable=datetime.timedelta(seconds=15*60))

        self.assertEqual(Task.objects.all().total_billable_time(), datetime.timedelta(seconds=3*15*60))
        self.assertEqual(Task.objects.filter(description='a').total_billable_time(), datetime.timedelta(seconds=2*15*60))
        self.assertEqual(f.task_set.total_billable_time(), datetime.timedelta(seconds=2*15*60))

class TaskFormTest(TestCase):

    def test_create_task_with_known_file_reference(self):
        file = File.objects.create(reference='abc')
        form = TaskForm({
            'reference': 'abc',
            'description': 'task description',
        })
        form.is_valid()
        task = form.save()
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(task.file, file)

    def test_create_task_with_unknown_file_reference(self):
        form = TaskForm({
            'reference': 'abcdef',
            'description': 'task description',
        })
        form.is_valid()
        task = form.save()
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(File.objects.count(), 1)
        self.assertEqual(task.file.reference, 'abcdef')

    def test_create_task_with_empty_file_reference(self):
        # Creates no file, if reference is empty
        form = TaskForm({
            'reference': '',
            'description': 'task description',
        })
        form.is_valid()
        task = form.save()
        self.assertEqual(Task.objects.count(), 1)
        self.assertIsNone(task.file)

    def test_max_length_reference(self):
        form = TaskForm({
            'reference': 'a'*129, # invalid
            'description': 'valid',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('reference', form.errors)

    def test_empty_description(self):
        form = TaskForm({
            'reference': '123',
            'description': '' # invalid
        })
        self.assertFalse(form.is_valid())
        self.assertIsNotNone(form.errors['description'])

    def test_reference_widget_template(self):
        form = TaskForm()
        widget = form.fields['reference'].widget
        self.assertEqual(widget.template_name, 'timesheet/forms/widgets/datalist_input.html')

    def test_reference_widget_choices(self):
        File.objects.create(reference='foo')
        form = TaskForm()
        widget = form.fields['reference'].widget
        self.assertListEqual(list(widget.choices), [('foo', 'foo')])
 
    def test_widget_context(self):
        File.objects.create(reference='foo')
        form = TaskForm()
        widget = form.fields['reference'].widget
        context = widget.get_context('foo', 'bar', {})
        self.assertEqual(context['widget']['datalist'], [('foo', 'foo')])

    def test_render_reference_field(self):
        File.objects.create(reference='foo')
        form = TaskForm()
        html = '{}'.format(form['reference'])
        self.assertIn('input', html)
        self.assertIn('datalist', html)
        self.assertIn('id="reference_datalist"', html)
        self.assertIn('list="reference_datalist"', html)
        self.assertIn('<option value="foo">', html)

    def test_render_description_field(self):
        form = TaskForm()
        html = '{}'.format(form['description'])
        self.assertNotIn('required', html)

    def test_initial_reference(self):
        form = TaskForm(initial={'reference': 'foo'})
        self.assertEqual(form['reference'].value(), 'foo')

class TimesheetViews(TestCase):

    def test_home_page(self):

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'timesheet/index.html')

    def test_create_file_and_task_on_home_page(self):

        response = self.client.post(reverse('index'), data={'reference': 'abc', 'description': 'task'})
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(File.objects.first().reference, 'abc')
        self.assertEqual(File.objects.first().task_set.first().description, 'task')

    def test_create_task_with_empty_description(self):

        response = self.client.post(reverse('index'), data={'reference': 'abc', 'description': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'].errors['description'])

    def test_update_file(self):
        file = File.objects.create(reference='a')
        response = self.client.get(reverse('file', args=(file.pk,)))
        self.assertTemplateUsed('timesheet/file_form.html')        
        response = self.client.post(reverse('file', args=(file.pk,)), data={'reference': 'b'})
        self.assertRedirects(response, file.get_absolute_url())
        file.refresh_from_db()
        self.assertEqual(file.reference, 'b')
        
    def test_create_task_from_file(self):

        file = File.objects.create()
        response = self.client.get(reverse('create_task', args=(file.pk,)))
        self.assertEqual(response.context['form'].initial['file'], file.pk)

    def test_update_task(self):
        task = Task.objects.create(description='a')
        response = self.client.get(reverse('task', args=(task.pk,)))
        self.assertTemplateUsed('timesheet/task_form.html')        
        response = self.client.post(reverse('task', args=(task.pk,)),
            data={'description': 'b', 'min_billable_time':datetime.timedelta(seconds=15*60)})
        self.assertRedirects(response, task.get_absolute_url())
        task.refresh_from_db()
        self.assertEqual(task.description, 'b')

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

    def test_list_files(self):

        File.objects.create(reference='a123')
        File.objects.create(reference='b1234')
        File.objects.create(reference='c1234')

        response = self.client.get(reverse('file_list'))
        self.assertEqual(response.context['object_list'].count(), 3)

        # Search list
        response = self.client.get(reverse('file_list'), data={'reference': '1234'})
        self.assertEqual(response.context['object_list'].count(), 2)

        # A single hit redirects to the file itself 
        response = self.client.get(reverse('file_list'), data={'reference': 'a'})
        self.assertRedirects(response, File.objects.first().get_absolute_url())

    def test_set_billable_time(self):
        task = Task.objects.create()
        task.timer.start()
        sleep(0.1)
        task.timer.stop()
        response = self.client.post(reverse('set_billable_time', args=(task.pk,)))
        task.refresh_from_db()
        self.assertTrue(task.billable > datetime.timedelta(seconds=0))
        self.assertRedirects(response, task.get_absolute_url())

    def test_export_monthly_task_list_as_pdf(self):
        t1=Task.objects.create()
        Task.objects.filter(pk=t1.pk).update(date=datetime.date(2017,1,1))

        response = self.client.get(reverse('task_archive_pdf', args=(2017, 1)))
        self.assertEqual(response.status_code, 200)
        
    def test_delete_task(self):
        t = Task.objects.create()

        response = self.client.get(reverse('delete_task', args=(t.pk,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('delete_task', args=(t.pk,)))
        self.assertRedirects(response, reverse('index'))

class TaskListTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        t1 = Task.objects.create(description='foo')
        Task.objects.filter(pk=t1.pk).update(date=datetime.date(2016,1,1))
        
        t2 = Task.objects.create(description='Obladi-oblada')
        Task.objects.filter(pk=t2.pk).update(date=datetime.date(2017,5,1))
        
        t3 = Task.objects.create(description='foobar')
        Task.objects.filter(pk=t3.pk).update(date=datetime.date(2018,1,1))

    def test_task_archive_index(self):

        response = self.client.get(reverse('task_archive'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['date_list'].count(), 3)
        self.assertEqual(response.context['object_list'].count(), 3)

    def test_filter_archive(self):
        response = self.client.get(reverse('task_archive'), data={'description': 'foo'})
        self.assertEqual(response.context['date_list'].count(), 3)
        self.assertEqual(response.context['object_list'].count(), 2)

    def test_year_archive(self):

        response = self.client.get(reverse('task_archive', args=(2017,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['date_list'].count(), 1)
        self.assertEqual(response.context['object_list'].count(), 1)
        self.assertContains(response, 'Obladi-oblada')
        self.assertTrue(hasattr(response.context['f'], 'form'))

    def test_month_archive(self):

        response = self.client.get(reverse('task_archive', args=(2017, 5)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 1)
