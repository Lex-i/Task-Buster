# -*- coding: utf-8 -*-
from django.db import models


class EmployeeManager(models.Manager):
    def subordinate_employees_list(self):
        user_list = []
        if self.department.supervisor == self:
            for item in self.department.department_staff:
                user_list.append((item.id, item.name))
        else:
            for item in self.subordinate_employees:
                user_list.append((item.id, item.name))
        return user_list


class ProjectManager(models.Manager):
    # The projects which are available for employee as a manager
    def available_for(self, employee):
        if employee.user.is_superuser:
            return self.all().order_by('name')
        else:
                # avail_projects = [i for i in self if employee.id == self.user]
            return employee.projects.all().order_by('name')

    def ProjectTasksHeirarchy(self, order):
        m = []
        for t in self.tasks.all().order_by(order):
            m.append(t)
            if t.parent_task in m:
                for i in range(len(m) - 2, 0, -1):
                    if t.parent_task == m[i - 1].id:
                        break
                    else:
                        m[i], m[i + 1] = m[i + 1], m[i]
        return m  # return the HDR or indent of each task in list


class DepartmentManager(models.Manager):
    pass


class TagManager(models.Manager):
    pass


class CommentManager(models.Manager):
    pass


class TaskManager(models.Manager):
    pass


class ProjectTeamManager(models.Manager):
    pass
    # All the tasks which are available for employee
    # def available_for(self, employee):
    #   if employee.user.is_superuser:
    #         return self.all().order_by('name')
    #     else:
    #       return employee.user.assigned_tasks.all().order_by('name')
