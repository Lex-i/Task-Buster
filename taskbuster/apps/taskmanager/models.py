# -*- coding: utf-8 -*-
from datetime import date
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import RegexValidator

from . import managers


# Read about Models: https://docs.djangoproject.com/en/2.0/topics/db/models/
class Employee(models.Model):
    # Relations
    user = models.OneToOneField(
        # The User model is imported using AUTH_USER_MODEL from settings.py.
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        # related_name is used to define how can you access
        # an employee instance from the user model.
        related_name="employee",
        # verbose_name is used to define a more readable name.
        # Note that this name is wrapped around the ugettext_lazy function
        verbose_name=_('user')
    )
    supervisor = models.ForeignKey(
        # The supervisor is a relative user who is a supervisor of the current one
        'self',
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='supervisor_of_user',
    )
    department = models.ForeignKey(
        # The supervisor is a relative user who is a supervisor of the current one
        'Department',
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='Department',
    )
    # Attributes - Mandatory
    name = models.CharField(
        max_length=100,
        verbose_name=_("Full name"),
        help_text=_("Enter the employee's name")
    )
    int_phone = models.PositiveIntegerField(
        default=100,
        help_text=_("Enter the internal phone number")
    )
    ext_phone = models.CharField(
        max_length=12,
        help_text=_("Enter the external (mobile) phone number")
    )
    job_title = models.CharField(
        max_length=100,
        help_text=_("Enter the employee's job title")
    )
    interaction = models.PositiveIntegerField(
        default=0,
        verbose_name=_("interaction")
    )
    # Attributes - Optional
    # The Object Manager is used to make queries
    objects = managers.EmployeeManager()

    # Custom Properties
    @property
    def username(self):
        return self.user.username

    # @property
    # def employee_info(self):
    #     "Returns the person's full name."
    #     return '{} {} {} {}'.format(
    #         self.user.name,
    #         self.user.job_title,
    #         self.user.int_phone,
    #         phone_format(self.user.ext_phone)
    #     )

    # Methods

    # Meta and String
    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
        ordering = ("name",)

    def __str__(self):
        return self.user.username


class Department(models.Model):
    # Attributes - Mandatory
    name = models.CharField(
        max_length=100,
        default=1,
        verbose_name=_("Department name"),
        help_text=_("Enter the Department name")
    )
    # Relations
    supervisor = models.ForeignKey(
        # The supervisor is a relative user who is a supervisor of the current one
        Employee,
        # on_delete=models.CASCADE,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='supervisor_of_department',
    )
    # Attributes - Optional
    # number = models.PositiveIntegerField(
    #     default=0,
    #     help_text=_("Enter the Department number")
    # )
    # Object Manager
    objects = managers.DepartmentManager()
    # Custom Properties
    # Methods

    # Meta and String
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        ordering = ("name",)

    def __str__(self):
        return self.name
    # pass


class Project(models.Model):
    # Relations
    user = models.ForeignKey(
        Employee,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="projects",
        verbose_name=_("Project Manager")
    )
    # Attributes - Mandatory
    name = models.CharField(
        max_length=120,
        verbose_name=_("name"),
        help_text=_("Enter the project name")
    )
    # Attributes - Optional
    color = models.CharField(
        max_length=7,
        default="#fff",
        validators=[RegexValidator(
            "(^#[0-9a-fA-F]{3}$)|(^#[0-9a-fA-F]{6}$)")],
        verbose_name=_("color"),
        help_text=_("Enter the hex color code, like #ccc or #cccccc")
    )
    description = models.TextField(
        verbose_name=_("Description"),
        # models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Enter description")
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name=_("Priority"),
        default=1,
        help_text=_("Enter the priority of the project")
    )
    softdeadline = models.DateField(
        verbose_name=_("Soft deadline"),
        default=date.today,
        help_text=_("Enter the soft deadline")
    )
    harddeadline = models.DateField(
        verbose_name=_("Hard deadline"),
        default=date.today,
        help_text=_("Enter the hard deadline")
    )
    # Object Manager
    objects = managers.ProjectManager()
    # Custom Properties
    # Methods

    # Meta and String
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ("priority", "name")
        # unique_together = ("user", "name")

    def __str__(self):
        return self.name  # "%s - %s" % (self.user, self.name)


class Comment(models.Model):
    # Relations
    project = models.ForeignKey(
        Project,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="comments",
        verbose_name=_("project")
    )
    user = models.ForeignKey(
        Employee,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="employee",
        verbose_name=_("employee")
    )
    # Attributes - Mandatory
    text = models.TextField(
        verbose_name=_("Description"),
        # models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Enter description")
    )
    datetime = models.DateTimeField(
        verbose_name=_("Date & time"),
        auto_now_add=True,
    )
    # Object Manager
    objects = managers.CommentManager()
    # Custom Properties
    # Methods

    # Meta and String
    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ("project", "user")
        unique_together = ("project", "user")

    def __str__(self):
        return "%s - %s" % (self.project, self.user)


class Tag(models.Model):
    # Relations
    user = models.ForeignKey(
        Employee,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="tags",
        verbose_name=_("user")
    )
    # Attributes - Mandatory
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name")
    )
    # Attributes - Optional
    # Object Manager
    objects = managers.TagManager()
    # Custom Properties
    # Methods

    # Meta and String
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ("user", "name",)
        # unique_together = ("user", "name")

    def __str__(self):
        return self.name  # "%s - %s" % (self.user, self.name)


class Task(models.Model):
    # Relations
    project = models.ForeignKey(
        Project,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="tasks",
        verbose_name=_("project")
    )
    parenttask = models.ForeignKey(
        # The parenttask is a relative task which is a higher level task of the current one
        'self',
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='parent_task',
        verbose_name=_("Parent task")
    )
    resources = models.ManyToManyField(
        Employee,
        through='TaskResources',
        through_fields=('task', 'employee'),
    )
    tags = models.ManyToManyField(
        Tag,
        through='TaskTags',
        through_fields=('task', 'tag')
    )
    # Attributes - Mandatory
    name = models.CharField(
        max_length=120,
        verbose_name=_("name"),
        help_text=_("Enter the project name")
    )
    # Attributes - Optional
    completed = models.BooleanField(
        default=False,
        verbose_name=_("completed")
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name=_("Priority"),
        default=1,
        help_text=_("Enter the priority of the task")
    )
    due_date = models.DateField(
        verbose_name=_("Due date"),
        default=date.today,
        help_text=_("Enter the planned due date")
    )
    completed_date = models.DateField(
        verbose_name=_("Completed date"),
        # models.SET_NULL,
        blank=True,
        null=True
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        null=True,
        help_text=_("Enter description")
    )
    # Object Manager
    objects = managers.TaskManager()
    # Custom Properties
    # Methods

    # Meta and String
    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        ordering = ("priority", "name")
        # unique_together = ("user", "name")

    def __str__(self):
        return self.name  # "%s - %s" % (self.user, self.name)


class TaskResources(models.Model):
    task = models.ForeignKey(Task,
                             on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee,
                                 on_delete=models.CASCADE)
    appointer = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='supervisor_appoints'
    )
    appointment_reason = models.CharField(max_length=64)


class TaskTags(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
# def phone_format(n):
#     return format(int(n[:-1]), ",").replace(",", "-") + n[-1]


# Django signals
''' The first one checks if a new instance of the User model has been created,
    and if true, it creates a Employee instance
    using the new user instance. '''


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_employee_for_new_user(sender, created, instance, **kwargs):
    if created:
        employee = Employee(user=instance)
        employee.save()
