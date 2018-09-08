# -*- coding: utf-8 -*-
from django.contrib import admin
from . import models


class ProjectsInLine(admin.TabularInline):
    model = models.Project
    extra = 0


class TasksInLine(admin.TabularInline):
    model = models.Task
    extra = 0


class EmployeesInLine(admin.TabularInline):
    model = models.Employee
    extra = 0


class TagsInLine(admin.TabularInline):
    model = models.Tag
    extra = 0


class CommentsInLine(admin.TabularInline):
    model = models.Comment
    extra = 0


class ProjectTeamInLine(admin.TabularInline):
    model = models.ProjectTeam
    extra = 0


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        # "username",
        "name",
        "job_title",
        "int_phone",
        "ext_phone",
        "_supervisor",
        'department',
        "_projects",
        "_tags"
    )

    search_fields = ["name"]

    inlines = [
        ProjectsInLine, TagsInLine
    ]

    def _projects(self, obj):
        return obj.projects.all().count()

    def _supervisor(self, obj):
        return obj.name

    def _tags(self, obj):
        return obj.tags.all().count()


@admin.register(models.Department)
class DeparmentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "_supervisor"
    )

    search_fields = ["name"]

    inlines = [
        EmployeesInLine
    ]

    def _supervisor(self, obj):
        return obj.supervisor.name


@admin.register(models.Project)
class ProjectsAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "_supervisor",
        "priority",
        "softdeadline",
        "harddeadline",
        "_tasks",
        "_comments"
    )

    search_fields = ["name"]

    inlines = [
        ProjectTeamInLine, TasksInLine, CommentsInLine
    ]

    def _supervisor(self, obj):
        return obj.user.name

    def _tasks(self, obj):
        return obj.related_tasks.all().count()

    def _comments(self, obj):
        return obj.related_comments.all().count()


@admin.register(models.Task)
class TasksAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "owner",
        "priority",
        "due_date",
        "completed",
        "assigned_to",
        "project",
        
    )

    search_fields = ["name"]

    # inlines = [TasksInLine]