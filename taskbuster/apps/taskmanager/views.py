# from django.shortcuts import render
# from django.forms import ModelForm
# from django import forms
from django.contrib.auth.models import User
# from django.conf import settings
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, QueryDict
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.urls import reverse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from taskmanager.models import *
from taskmanager.forms import *
from taskmanager.managers import *
# from django.contrib.auth.forms import AuthenticationForm
# from django.utils import timezone
from django.core.paginator import Paginator

'''
# login view
def home(request):
    f = AuthenticationForm()
    if request.method == 'POST':
        f = AuthenticationForm(request.POST)
        if f.is_valid():
            f.save(commit=True)
            return HttpResponseRedirect(reverse('tasks_list'))
    return render(request, 'base.html', {'lform': f})
'''
# Create your views here.


@login_required
def index(request):
    return HttpResponseRedirect(reverse('tasks_list'))

# The Task List
# Access: everyone can see the tasks which project they are in; admins


@login_required
def todo_list(request, state=0):
    order = direct = ''
    project = None
    owner = None
    search_name = None
    filter_on = False
    search_name_off = True
    # user = request.user.employee

    # get projects and task, that user has access to
    projects = Project.objects.available_for(request.user.employee)
    tasks = Task.objects.filter(project__in=projects).filter(
        assigned_to__id=request.user.employee.id)

    # Users for filter
    owners = Employee.objects.all().order_by('name')
    users = ProjectTeam.objects.filter(project__in=projects)

    # Save project_id in session, if it has been recieved via GET
    if request.GET.get('project_id', False):
        try:
            project_id = int(request.GET['project_id'])
        except project_id:
            raise Http404
        if project_id != 0:
            project = get_object_or_404(Project, pk=project_id)
        request.session['project_id'] = project_id

    # Save owner_id in session, if it has been recieved via GET
    if request.GET.get('owner_id', False):
        try:
            owner_id = int(request.GET['owner_id'])
        except owner_id:
            raise Http404
        if owner_id != 0:
            owner = get_object_or_404(Employee, pk=owner_id)
        request.session['owner_id'] = owner_id

    if request.GET.get('search_name_off', False):
        del request.session['search_name']

    # Save search_name in session, if it has been recieved via GET
    if request.GET.get('search_name', False):
        try:
            search_name = request.GET['search_name']
        except search_name:
            raise Http404
        # if search_name != "":
        #     search_name = get_object_or_404(Task, name__icontains=search_name)
        request.session['search_name'] = search_name

    # Save a group of tasks (incoming, outcoming, everyone) and sorting, if they have been recieved via GET
    '''
    if request.GET.get('folder', False):
        request.session['folder'] = request.GET['folder']
    if request.GET.get('order', False):
        request.session['order'] = request.GET['order']
    if request.GET.get('dir', False):
        request.session['dir'] = request.GET['dir']
    '''

    # If the group of tasks or filter settings have been changed or deleted,
    # then delete all existing
    # (request.GET.get('filter_on', False) in ('on', 'off')):
    if request.GET.get('filter_on', False):
        for key in ('owner_id', 'assigned_to', 'parenttask', 'search_name', 'project_id'):
            try:
                del request.session[key]
            except KeyError:
                pass
        tasks = Task.objects.filter(project__in=projects).filter(
            assigned_to__id=request.user.employee.id)
        project = None
        owner = None
        search_name = None
        return HttpResponseRedirect(reverse('tasks_list'))

    if request.GET.get('search_name_off', False):
        try:
            del request.session['search_name']
            del request.session['search_name_off']
        except KeyError:
            pass

    # Save additional filter parameters in session
    '''
    if request.GET.get('filter', False) == 'on':
        if request.GET.get('owner', False):
            request.session['owner'] = request.GET['owner']
        if request.GET.get('assigned_to', False):
            request.session['assigned_to'] = request.GET['assigned_to']
        if request.GET.get('parenttask', False):
            request.session['parenttask'] = request.GET['parenttask']
        if request.GET.get('search_name', False):
            request.session['search_name'] = request.GET['search_name']
    '''

    params = request.session

    # delete filter
    if params.get('filter_on', False):
        project = None
        owner = None
        search_name = None
        tasks = Task.objects.filter(project__in=projects).filter(
            assigned_to__id=request.user.employee.id)
        return todo_list(request)
    else:
        # filter by project
        if params.get('project_id', False):
            if params['project_id'] != '0':
                params['project_id'] = int(params['project_id'])
                try:
                    project = Project.objects.get(pk=params['project_id'])
                    if not project.is_avail(request.user.employee):
                        request.session['project_id'] = '0'
                        return HttpResponseRedirect(reverse('tasks_list'))
                    else:
                        tasks = tasks.filter(project__id=params['project_id'])
                except Project.DoesNotExist:
                    request.session['project_id'] = '0'

        # filter by owner
        if params.get('owner_id', False):
            if params['owner_id'] != '0':
                params['owner_id'] = int(params['owner_id'])
                try:
                    owner = Employee.objects.get(pk=params['owner_id'])
                    tasks = tasks.filter(owner__id=params['owner_id'])
                except Owner.DoesNotExist:
                    request.session['owner_id'] = '0'

        # filter by Name
        if params.get('search_name_off', False):
            search_name = None
            tasks = tasks.filter(name=any)
        else:
            if params.get('search_name', False):
                search_name = params['search_name']
                tasks = tasks.filter(name__icontains=params['search_name'])

    # filter by group
    '''
    if params.get('folder', False):
        folder = params['folder']
        if not (folder == 'inbox' or folder == 'outbox' or folder == 'all'):
            folder = 'inbox'
    else:
        folder = 'inbox'

    if folder == 'inbox':
        tasks = tasks.filter(assigned_to=request.user.employee)
    elif folder == 'outbox':
        tasks = tasks.filter(owner=request.user.employee)

    # additional filter

    if ((params.get('owner', False) and not folder == 'outbox') or
        (params.get('assigned_to', False) and not folder == 'inbox') or
            params.get('parenttask', False) or params.get('search_name', False)):
        filter_on = True
        # Owner
        if params.get('owner', False) and not folder == 'outbox':
            try:
                params['owner'] = int(params['owner'])
                tasks = tasks.filter(owner__id=params['owner'])
            except ValueError:
                pass
        # Task assignee
        if params.get('assigned_to', False) and not folder == 'inbox':
            try:
                params['assigned_to'] = int(params['assigned_to'])
                tasks = tasks.filter(assigned_to__id=params['assigned_to'])
            except ValueError:
                pass
        # Parent Task
        if params.get('parenttask', False):
            try:
                params['parenttask'] = int(params['parenttask'])
                tasks = tasks.filter(parenttask__id=params['parenttask'])
            except ValueError:
                pass
        # Title
        if params.get('search_name', False):
            tasks = tasks.filter(name__icontains=params['search_name'])
    '''
    # Sorting
    if params.get('order', False):
        order = params['order']
    else:
        order = 'created_at'
    if params.get('dir', False):
        direct = params['dir']
    else:
        direct = 'desc'

    if order == 'created_at':
        if direct == 'desc':
            tasks = tasks.order_by('-created_at')
        else:
            tasks = tasks.order_by('created_at')
    elif order == 'priority':
        if direct == 'desc':
            tasks = tasks.order_by('-priority', '-created_at')
        else:
            tasks = tasks.order_by('priority', '-created_at')
    elif order == 'due_date':
        if direct == 'desc':
            tasks = tasks.order_by('completed', '-due_date', '-created_at')
        else:
            tasks = tasks.order_by('-completed', 'due_date', '-created_at')
    elif order == 'project':
        if direct == 'desc':
            tasks = tasks.order_by('-project__name', '-created_at')
        else:
            tasks = tasks.order_by('project__name', '-created_at')
    elif order == 'task':
        if direct == 'desc':
            tasks = tasks.order_by('-name', '-created_at')
        else:
            tasks = tasks.order_by('name', '-created_at')
    elif order == 'completed_date':
        if direct == 'desc':
            tasks = tasks.order_by(
                '-completed', '-completed_date', '-created_at')
        else:
            tasks = tasks.order_by(
                'completed', 'completed_date', '-created_at')
    elif order == 'assigned_to':
        if direct == 'desc':
            tasks = tasks.order_by('-assigned_to__name', '-created_at')
        else:
            tasks = tasks.order_by('assigned_to__name', '-created_at')
    elif order == 'owner':
        if direct == 'desc':
            tasks = tasks.order_by('-owner__name', '-created_at')
        else:
            tasks = tasks.order_by('owner__name', '-created_at')
    else:
        order = 'created_at'
        direct = 'desc'
        tasks = tasks.order_by('-created_at')

    # Split into pages
    paginator = Paginator(tasks, 100)
    page_num = int(request.GET.get('page', '1'))
    page = paginator.page(page_num)

    return render(request, 'taskbuster/todo_list.html',
                  {'tasks': page.object_list,
                   'page': page,
                   'paginator': paginator,
                   'current_page': page_num,
                   'projects': projects,
                   'project': project,
                   'params': params,
                   # 'folder': folder,
                   'order': order,
                   'dir': direct,
                   'menu_active': 'tasks',
                   # 'user': user,
                   'users': users,
                   'owners': owners,
                   'owner': owner,
                   'search_name': search_name,
                   'search_name_off': search_name_off,
                   # 'states': states,
                   'filter_on': filter_on
                   })


# information about task
# Access: project team, admins
@login_required
def details(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if not task.project.is_avail(request.user.employee):
        return HttpResponseForbidden()

    return render(request, 'taskbuster/task_details.html', {'task': task, 'menu_active': 'tasks'})


# Task edition
# Access: owner, admins
@login_required
def edit(request, task_id):
    # task = get_object_or_404(Task, pk=task_id)
    task = Task.objects.get(pk=task_id)
    project = task.project
    p_id = task.project_id
    print(task_id)
    if not task.project.is_avail(request.user.employee):
        return HttpResponseForbidden()

    owner = task.owner
    if not (request.user.employee == owner):  # request.user.has_perm('taskbuster.change_task') or
        return HttpResponseForbidden()

    if request.method == 'POST':
        f = TaskForm(request.user, project, request.POST, instance=task)
        if f.is_valid():
            t = f.save(commit=False)
            t.owner = request.user.employee
            t.project = project
            t.save()
            return HttpResponseRedirect(reverse('project_details', args=(p_id,)))
    else:
        f = TaskForm(request.user, project, instance=task)

    # projects = Project.objects.available_for(request.user.employee)
    # users = task.project.users.all().order_by('name')

    return render(request, 'taskbuster/task_edit.html',
                  {'form': f, 'task': task, 'p': project, 'menu_active': 'tasks'})


# Add a task
# Access: project team, admins
@login_required
def add_task(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    f = TaskForm(request.user.employee, project)
    owner = request.user.employee
    # projects = Project.objects.available_for(request.user)
    # if not projects:
    if request.user.employee not in project.users.all():
        return render(request, 'taskbuster/task_edit.html',
                      {'no_available_projects': True,
                       'menu_active': 'tasks', 'add': True})

    if request.method == 'POST':
        f = TaskForm(request.user.employee, project, request.POST)
        if f.is_valid():
            # if not f.cleaned_data['project'].is_avail(request.user.employee):
            #     return HttpResponseForbidden()
            # f.save(commit=True)
            t = f.save(commit=False)
            t.owner = request.user.employee
            t.project = project
            t.save()

            # assigned_to_id = request.POST.get('assigned_to', '')
            # if assigned_to_id:
            #     t.assigned_to = User.employee.objects.get(pk=assigned_to_id)
            #     t.save()
            #     t.mail_notify(request.get_host())
            return HttpResponseRedirect(reverse(
                'project_details', args=(project_id,)))
        else:
            print(f.errors)
        # init_data = {
        #     'project': request.session.get('project_id', ''),
        # }
        # f = TaskForm(request.user.employee, initial=init_data)

    # users = users_in_projects(projects)

    return render(request, 'taskbuster/task_edit.html',
                  {'form': f, 'add': True, 'owner': owner, 'menu_active': 'tasks'})


# Delete a task
# Access: owner admins
@login_required
def delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if not task.project.is_avail(request.user.employee):
        return HttpResponseForbidden()

    owner = get_object_or_None(User.employee, id=task.owner_id)
    if not (request.user.has_perm('taskbuster.delete_task') or request.user.employee == owner):
        return HttpResponseForbidden()

    if task.completed:
        return HttpResponseForbidden()

    task.delete()
    return HttpResponseRedirect(reverse('tasks_list'))


# Project list
# Access: project team member; admins
@login_required  # @render_to('taskbuster/projects_list.html')
def projects_list(request, state=0):
    # project = None
    projects = Project.objects.available_for(request.user.employee)
    # # Save project_id in session, if it has been recieved via GET
    # if request.GET.get('project_id', False):
    #     try:
    #         project_id = int(request.GET['project_id'])
    #     except project_id:
    #         raise Http404
    #     if project_id != 0:
    #         project = get_object_or_404(Project, pk=project_id)
    #     request.session['project_id'] = project_id
    # params = request.session
    # # filter by project
    # if params.get('project_id', False):
    #     if params['project_id'] != '0':
    #         params['project_id'] = int(params['project_id'])
    #         try:
    #             project = Project.objects.get(pk=params['project_id'])
    #         except Project.DoesNotExist:
    #             request.session['project_id'] = '0'
    return render(request, "taskbuster/projects_list.html", {
        'projects': projects,
        # 'project': project,
        'menu_active': 'projects'})


# Project info
# Accees: project team member; admins
@login_required
def project_details(request, project_id):
    user = request.user.employee
    project = get_object_or_404(Project, pk=project_id)
    tasks = project.related_tasks.all().order_by('due_date')
    m = []
    pm = False
    if request.user.employee == project.user:
        pm = True

    # for t in tasks:
    #     if not t.parenttask:
    #         m.append(t)
    #         for st in t.subtasks.all().order_by('due_date'):
    #             m.append(st)
    #             m[len(m) - 1].name = ' ╚ ' + st.name

    if not project.is_avail(request.user.employee):
        return HttpResponseForbidden()

    return render(request, "taskbuster/project_details.html", {
        'project': project,
        'tasks': tasks,
        'm': m,
        'pm': pm,
        'menu_active': 'projects'
    })


# Add project
# Access: project managers, admins
@login_required
def add_project(request):
    employees = Employee.objects.order_by('name')
    f = ProjectForm()
    # f = ProjectFormSet()
    if not request.user.is_superuser and request.user.employee.job_title != 'Project manager':
        return HttpResponseForbidden('You can not add a project')

    if request.method == 'POST':
        f = ProjectForm(request.POST)
        # f = ProjectFormSet(request.POST)
        if f.is_valid():
            f.save(commit=True)
            # prj.save()
            # for member in prj:
            #     projectteam = ProjectTeam(project=prj)
            #     projectteam.employee = prj.users
            #     projectteam.save()
            # f.save_m2m()
            #             team = f.fields['users']
            # f.fields['users'] = None
            # prj = f.save(commit=False)
            # prj.save()
            # # f.save_m2m()
            # # m2m_changed.connect(Project, sender=Project)

            # @receiver(post_save, sender=Project)
            # def create_projectteam(sender, created, team, instance, **kwargs):
            #     # global team
            #     if created:
            #         for m in team.queryset:
            #             ProjectTeam.objects.create(employee=m, project=prj)
            #         projectteam = ProjectTeam(project=instance)
            #         # ProjectTeam.project=project.id
            #         projectteam.employee = instance.user
            #         projectteam.save()

            return HttpResponseRedirect(reverse('team_edit', args=(project_id,))) # projects_list(request)
        else:
            print(f.errors)
    # else:
    #     f = ProjectForm(request.user)

    return render(request, 'taskbuster/project_edit.html', {'form': f, 'add': True, 'employees': employees})


# EDIT PROJECT TEAM
# Access: project managers, admins
@login_required
def team_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    users = Employee.objects.all().order_by('name')
    if not request.user.is_superuser and request.user.employee != project.user:
        return HttpResponseForbidden()
    pm = project.user
    team_id = []
    oldteam = {}

    for user in users:
        try:
            member = ProjectTeam.objects.get(employee=user.id, project=project)
            team_id.append(user.id)
            oldteam.update({user.id: 'on'})
        except ProjectTeam.DoesNotExist:
            oldteam.update({user.id: 'off'})

    if request.method == 'POST':
        for user in users:
            if user != project.user:
                try:
                    if request.POST[str(user.id)] == 'on' and oldteam[user.id] == 'off':
                        a = ProjectTeam(employee=get_object_or_404(
                            Employee, pk=user.id), project=project)
                        a.save()
                except:
                    if oldteam[user.id] == 'on':
                        ProjectTeam.objects.filter(employee=get_object_or_404(
                            Employee, pk=user.id), project=project).delete()
        return HttpResponseRedirect(reverse('project_details', args=(project_id,)))

    return render(request, 'taskbuster/team_edit.html',
                  {'users': users, 'team': team_id, 'old_team': oldteam, 'project': project, 'pm': pm})


# EDIT PROJECT
# Access: project managers, admins
@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if not request.user.is_superuser and request.user.employee != project.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        f = ProjectForm(request.POST, instance=project)
        if f.is_valid():
            f.save(commit=True)
            # p.save()
            # f.save_m2m()
            return HttpResponseRedirect(reverse(
                'project_details', args=(project_id,)))
    else:
        f = ProjectForm(instance=project)

    return render(request, 'taskbuster/project_edit.html',
                  {'form': f, 'project': project, 'menu_active': 'projects'})

# Delete project
# Access: admins


@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if not project.is_avail(request.user.employee):
        return HttpResponseForbidden()

    if not (request.user.employee == project.user):
        return HttpResponseForbidden("You are not the project's manager")

    if project.tasks_count > 0:
        return render(request, 'taskbuster/project_delete_cannot.html',
                      {'project': project, 'menu_active': 'projects'})
    else:
        project.delete()
        return HttpResponseRedirect(reverse('projects_list'))


# Accept a task
# access: assigned_to
@login_required
def task_is_accepted(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    assigned_to = get_object_or_None(Employee, id=task.assigned_to_id)
    if not request.user.employee == assigned_to:
        return HttpResponseForbidden()

    # task.status = Status.objects.get(pk=2)
    task.save()
    # task.mail_notify(request.get_host())

    return HttpResponseRedirect(reverse('task_details', args=(task_id,)))

# COMPLETE TASK
# Access: assigned_to


@login_required
def task_is_completed(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    assigned_to = get_object_or_None(Employee, id=task.assigned_to_id)
    if not request.user.employee == assigned_to:
        return HttpResponseForbidden()

    # task.status = Status.objects.get(pk=3)
    task.completed = True
    task.save()
    # task.mail_notify(request.get_host())

    return HttpResponseRedirect(reverse('task_details', args=(task_id,)))

# Approve task result
# Access: owner


@login_required
def task_is_checked(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    author = get_object_or_None(Employee, id=task.author_id)
    if not request.user.employee == author:
        return HttpResponseForbidden()

    # task.status = Status.objects.get(pk=4)
    task.save()
    # task.mail_notify(request.get_host())

    return HttpResponseRedirect(reverse('task_details', args=(task_id,)))


# reassign the task
# Access: owner
@login_required
def task_is_reassigned(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    author = get_object_or_None(Employee, id=task.author_id)
    if not request.user.employee == author:
        return HttpResponseForbidden()

    # task.status = Status.objects.get(pk=1)
    task.completed = False
    task.save()
    # task.mail_notify(request.get_host(), True)
    return HttpResponseRedirect(reverse('task_details', args=(task_id,)))


# Add comment
# Access: project team member
@login_required
def add_comment(request, project_id):
    if request.method == 'POST' and request.POST.get('message', '') != '':
        project = get_object_or_404(Project, pk=project_id)

        if not project.is_avail(request.user.employee):
            return HttpResponseForbidden()

        text = request.POST.get('message', '')
        comment = Comment(author=request.user.employee,
                          project=project, text=text)
        if request.POST.get('reply_to', False):
            try:
                reply_to_id = int(request.POST['reply_to'])
                try:
                    comment.reply_to = Comment.objects.get(pk=reply_to_id)
                except Comment.DoesNotExist:
                    pass
            except ValueError:
                pass
        comment.save()
        # comment.mail_notify(request.get_host())

    return HttpResponseRedirect(reverse('project_details', args=(project_id,)) + '#comment_form')

# Edit comment
# Access: author


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    author = get_object_or_None(Employee, id=comment.author_id)
    if not comment.project.is_avail(request.user.employee):
        return HttpResponseForbidden()

    if not (request.user.employee.has_perm('taskbuster.edit_comment') or request.user.employee == author):
        return HttpResponseForbidden()
    if request.POST.get('message', ''):
        comment = Comment(author=request.user.employee,
                          project=project, text=text)
        comment.save
    else:
        comment.delete()
    return HttpResponseRedirect(reverse('project_details', args=(comment.project.id,)))


# The list of user which have acces to the project, in JSON
# use it in task form, uploade in 'assigned_to' for selected project.
# there is a list of users (project team, admins) if a project is selected.
# there is a list of users (from teams all project that the current user has accesse to)
# if a project is not selected
@login_required
def json_project_team(request):
    if request.GET.get('id', '') != '':
        project_id = request.GET['id']
        projects = get_list_or_404(Project, pk=project_id)
        if not projects[0].is_avail(request.user.employee):
            return HttpResponseForbidden()
    else:
        projects = Project.objects.available_for(request.user.employee)

    users = users_in_projects(projects)
    return render(request, 'taskbuster/json_project_team.html', {'users': users})

# 403 Forbidden page - access denied


@login_required
def forbidden(request, template_name='403.html'):
    t = loader.get_template(template_name)
    return HttpResponseForbidden(t.render(RequestContext(request)))
