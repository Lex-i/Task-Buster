# -*- coding: utf-8 -*-
from datetime import date
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
# from django.core.validators import RegexValidator

from . import managers


# users in project
def users_in_projects(projects):
    users = Employee.objects.filter(
        Q(project_team__in=projects) | Q(is_superuser=True)).distinct().order_by('name')
    return users


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
        verbose_name=_("Supervisor"),
        related_name='subordinate_employees',
    )
    department = models.ForeignKey(
        'Department',
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Department"),
        related_name='department_staff',
    )
    # Attributes - Mandatory
    name = models.CharField(
        max_length=100,
        verbose_name=_("Full name"),
        help_text=_("Enter the employee's name")
    )
    int_phone = models.PositiveIntegerField(
        default=100,
        verbose_name=_("Internal phone"),
        help_text=_("Enter the internal phone number")
    )
    ext_phone = models.CharField(
        max_length=12,
        verbose_name=_("External phone"),
        help_text=_("Enter the external (mobile) phone number")
    )
    job_title = models.CharField(
        max_length=100,
        verbose_name=_("Job title"),
        help_text=_("Enter the employee's job title")
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
        return self.name


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
        related_name='supervised_department',
        verbose_name=_("Supervisor"),
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
    users = models.ManyToManyField(
        Employee,
        through='ProjectTeam',
        through_fields=('project', 'employee'),
        verbose_name=_("Project Team member")
    )
    # Attributes - Mandatory
    name = models.CharField(
        max_length=120,
        verbose_name=_("Project Title"),
        help_text=_("Enter the project name")
    )
    # Attributes - Optional
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

    # Methods
    def __unicode__(self):
        return self.title

    def _get_tasks_count(self):
        return self.related_tasks.count()

    def _get_active_tasks_count(self):
        return self.related_tasks.exclude(completed=True).count()

    def _get_progress_statement(self):
        T = self.related_tasks.count()
        if T > 0:
            A = self.related_tasks.exclude(completed=True).count()
            return ((T - A) // T)
        else:
            return 0

    # Project is availiable for user

    def is_avail(self, employee):
        if employee.user.is_superuser:
            return True
        try:
            employee.avail_projects.get(project=self.pk)
            return True
        except Project.DoesNotExist:
            return False

    # User that has access to the project
    def allowed_users(self):
        pass
    # Custom Properties
    tasks_count = property(_get_tasks_count)
    active_tasks_count = property(_get_active_tasks_count)
    progress_statement = property(_get_progress_statement)

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
        related_name="related_comments",
        verbose_name=_("Project")
    )
    author = models.ForeignKey(
        Employee,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="written_comments",
        verbose_name=_("Author")
    )
    reply_to = models.ForeignKey(
        'self',
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='replies',
        verbose_name=_("In reply to")
    )
    # Attributes - Mandatory
    text = models.TextField(
        # models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Enter description"),
        verbose_name=_("Description"),
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
        ordering = ("datetime", )

    def __str__(self):
        return "%s - %s" % (self.author, self.datetime)


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
        verbose_name=_("Tag Name")
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
        related_name="related_tasks",
        verbose_name=_("project")
    )
    parenttask = models.ForeignKey(
        # The parenttask is a relative task which is a higher level task of the current one
        'self',
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='subtasks',
        verbose_name=_("Parent task")
    )
    owner = models.ForeignKey(
        Employee,
        models.SET_NULL,
        blank=True,
        null=True,
        # on_delete=models.CASCADE,
        related_name='owned_tasks',
        verbose_name=_("Task Owner")
    )
    assigned_to = models.ForeignKey(
        Employee,
        models.SET_NULL,
        blank=True,
        null=True,
        # on_delete=models.CASCADE,
        related_name='assigned_tasks',
        verbose_name=_("Task assignee")
    )
    tags = models.ManyToManyField(
        Tag,
        through='TaskTags',
        through_fields=('task', 'tag')
    )
    # Attributes - Mandatory
    name = models.CharField(
        max_length=120,
        verbose_name=_("Task Title"),
        help_text=_("Enter the task title")
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
    created_at = models.DateTimeField(
        verbose_name=_("Created date"),
        auto_now_add=True,
        blank=True,
        null=True
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

    def is_over_due(self):
        if self.due_date < date.today() and not self.completed:
            return True
        else:
            return False
    # Methods

    def complete_task(self):
        if self.completed:
            self.completed_date = date.today()
        if self.completed_date:
            self.completed = True
        return self
    # Meta and String

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        ordering = ("priority", "name")
        # unique_together = ("user", "name")

    def __str__(self):
        return self.name  # "%s - %s" % (self.user, self.name)


class ProjectTeam(models.Model):
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                related_name="project_team")
    employee = models.ForeignKey(Employee,
                                 on_delete=models.CASCADE,
                                 related_name="avail_projects",
                                 # verbose_name=_("Members")
                                 )

    # The Object Manager is used to make queries
    objects = managers.ProjectTeamManager()

    # Meta and String

    class Meta:
        verbose_name = _("member")
        verbose_name_plural = _("Project Team")
        # ordering = ("employee", "name")


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
        # employee = employee.create(user=instance)
        employee = Employee(user=instance)
        employee.name = instance.username
        employee.save()

# Add project manager into project team when project is created


@receiver(post_save, sender=Project)
def add_projectmanager_to_a_projectteam(sender, created, instance, **kwargs):
    if created:
        projectteam = ProjectTeam(project=instance)
        # ProjectTeam.project=project.id
        projectteam.employee = instance.user
        projectteam.save()

# Save a user as an owner when he is adding a task


# @receiver(post_save, sender=Task)
# def create_owner_for_new_task(sender, created, instance, **kwargs):
#     if created:
#         task = Task(id=instance)
#         task.owner = instance.user.employee
#         task.save()
