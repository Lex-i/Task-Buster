# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.core.urlresolvers import reverse

from django.contrib.auth import get_user_model
from . import models


# test when a new user is registered, it will trigger a function
# that creates a new employee instance
class TestEmployeeModel(TestCase):

    def test_employee_creation(self):
        User = get_user_model()
        # New user created
        user = User.objects.create(
            username="taskbuster", password="django-tutorial")
        # Check that a Employee instance has been crated
        self.assertIsInstance(user.employee, models.Employee)
        # Call the save method of the user to activate the signal
        # again, and check that it doesn't try to create another
        # employee instace
        user.save()
        self.assertIsInstance(user.employee, models.Employee)


class TestProjectModel(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(
            username="taskbuster", password="django-tutorial")
        self.employee = self.user.employee

    def tearDown(self):
        self.user.delete()

    def test_validation_color(self):
        # This first project uses the default value, #fff
        project = models.Project(
            user=self.employee,
            name="TaskManager"
        )
        self.assertTrue(project.color == "#fff")
        # Validation shouldn't rise an Error
        project.full_clean()

        # Good color inputs (without Errors):
        for color in ["#1cA", "#1256aB"]:
            project.color = color
            project.full_clean()

        # Bad color inputs:
        ValidationError = Exception
        for color in ["1cA", "1256aB", "#1", "#12", "#1234",
                      "#12345", "#1234567"]:
            with self.assertRaises(
                    ValidationError,
                    msg="%s didn't raise a ValidationError" % color):
                project.color = color
                project.full_clean()


class TestViews(TestCase):
    fixtures = ['taskbuster.json']

    def setUp(self):
        self.c = Client()

        # user pk=1
        User = get_user_model()
        self.user = User.objects.create(
            username="admin", password="password", is_superuser=1)
        self.employee = self.user.employee

        # user pk=2
        User = get_user_model()
        self.user = User.objects.create(
            username="tester", password="password", is_superuser=1)
        self.employee = self.user.employee

    def urltest(self, url, status_code):
        rs = self.c.get(url)
        self.failUnless(rs)
        print url
        self.assertEquals(rs.status_code,
                          status_code,
                          '%s returned %s, %s was expected' % (url,
                                                               rs.status_code,
                                                               status_code
                                                               )
                          )

    def test_user_urls(self):
        rs = self.c.post('/accounts/login/', {'username': 'admin', 'password': 'password'})
        self.failUnless(rs)

        urls = [
            ('/', 302),
            (reverse('add_task'), 200),
            (reverse('add_comment', args=(1,)), 302),
            (reverse('del_comment', args=(1,)), 302),
            (reverse('task_list'), 200),
            (reverse('task_details', args=(1,)), 200),
            (reverse('edit_task', args=(1,)), 200),
            (reverse('task_is_accepted', args=(1,)), 302),
            (reverse('task_is_completed', args=(1,)), 302),
            (reverse('task_is_checked', args=(1,)), 302),
            (reverse('task_is_reassigned', args=(1,)), 302),
            (reverse('delete_task', args=(1,)), 302),
            (reverse('projects_list'), 200),
            (reverse('add_project'), 200),
            (reverse('project_details', args=(2,)), 200),
            (reverse('edit_project', args=(2,)), 200),
            (reverse('json_project_team'), 200),
            (reverse('delete_project', args=(2,)), 302),
        ]

        for url in urls:
            self.urltest(url[0], url[1])

    def test_add_task(self):
        rs = self.c.post('/accounts/login/', {'username': 'admin', 'password': 'password'})
        self.failUnless(rs)

        rs = self.c.post(reverse('add_task'), {'project': '1', 'name': 'New task',
                                               'assigned_to': '1', 'due_date': '2008-12-12'})
        self.assertEquals(rs.status_code, 302)

        rs = self.c.post(reverse('add_task'), {'project': '1', 'name': 'One more',
                                               'assigned_to': '2', 'deadline': '2008-12-12'})
        self.assertEquals(rs.status_code, 302)

        rs = self.c.post(reverse('add_task'), {'project': '1', 'name': 'Not assigned task'})
        self.assertEquals(rs.status_code, 302)

        rs = self.c.post(reverse('add_task'), {'project': '1', 'name': 'New task', 'deadline': 'invalid_date'})
        self.assertEquals(rs.status_code, 200)

        rs = self.c.post(reverse('add_task'), {'project': '1', 'title': ''})
        self.assertEquals(rs.status_code, 200)

    def test_edit_task(self):
        rs = self.c.post('/accounts/login/', {'username': 'admin', 'password': 'password'})
        self.failUnless(rs)

        rs = self.c.post(reverse('edit_task', args=(1,)), {'project': '1', 'name': 'Edited task', 'assigned_to': '1'})
        self.assertEquals(rs.status_code, 302)

    def test_add_project(self):
        rs = self.c.post('/accounts/login/', {'username': 'admin', 'password': 'password'})
        self.failUnless(rs)

        rs = self.c.post(reverse('add_project'), {'name': 'New project'})
        self.assertEquals(rs.status_code, 302)

        rs = self.c.post(reverse('add_project'), {'name': ''})
        self.assertEquals(rs.status_code, 200)
