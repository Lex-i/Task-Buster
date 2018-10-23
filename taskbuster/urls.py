"""taskbuster URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import re_path, include  # , path
from django.conf.urls.i18n import i18n_patterns
from .views import home, home_files
from taskmanager.views import *
# + Note that we are using a relative import to import the home view.
# + This way, we can change the name of our project
# + or app without breaking the urls.

# + It makes robots.txt & humans.txt available for search engines at those urls
urlpatterns = [
    re_path(r'^(?P<filename>(robots.txt)|(humans.txt))$',
            home_files, name='home-files'),
    re_path(r'^accounts/', include('allauth.urls')),
]

# + internationalization
urlpatterns += i18n_patterns(
    re_path(r'^$', home, name='home'),
    re_path(r'^admin/', admin.site.urls),
)

urlpatterns += i18n_patterns(
    re_path(r'^tasks/$', todo_list, name='tasks_list'),
    # re_path(r'^tasks/new/$', add_task, name='add_task'),
    re_path(r'^tasks/(?P<task_id>\d+)/comments/new/$',
            add_comment, name='add_comment'),
    re_path(r'^tasks/edit_comment/(?P<comment_id>\d+)/$',
            edit_comment, name='edit_comment'),
    re_path(r'^tasks/(?P<task_id>\d+)/$',
            details, name='task_details'),
    re_path(r'^tasks/(?P<task_id>\d+)/edit/$',
            edit, name='edit_task'),
    re_path(r'^tasks/(?P<task_id>\d+)/delete/$',
            delete, name='delete_task'),
    re_path(r'^tasks/(?P<task_id>\d+)/is_accepted/$',
            task_is_accepted, name='task_is_accepted'),
    re_path(r'^tasks/(?P<task_id>\d+)/is_completed/$',
            task_is_completed, name='task_is_completed'),
    re_path(r'^tasks/(?P<task_id>\d+)/is_checked/$',
            task_is_checked, name='task_is_checked'),
    re_path(r'^tasks/(?P<task_id>\d+)/is_reassigned/$',
            task_is_reassigned, name='task_is_reassigned'),
    re_path(r'^projects/$', projects_list,
            name='projects_list'),
    re_path(r'^projects/new/$', add_project,
            name='add_project'),
    re_path(r'^projects/(?P<project_id>\d+)/$',
            project_details, name='project_details'),
    re_path(r'^projects/(?P<project_id>\d+)/add_task/$',
            add_task, name='add_task'),
    re_path(r'^projects/(?P<project_id>\d+)/team_edit/$',
            team_edit, name='team_edit'),
    re_path(r'^projects/(?P<project_id>\d+)/edit/$',
            edit_project, name='edit_project'),
    re_path(r'^projects/(?P<project_id>\d+)/delete/$',
            delete_project, name='delete_project'),
    re_path(r'^json/project_team/$',
            json_project_team, name='json_project_team'),
)
