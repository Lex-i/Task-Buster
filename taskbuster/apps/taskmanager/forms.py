from django.forms import ModelForm, Textarea, modelform_factory
from django import forms
# from django.contrib.auth.models import User
from taskmanager.models import *
# from taskmanager.templatetags.extras import username
from django.utils.translation import gettext_lazy as _


class OpenTaskmanagerModelForm(ModelForm):
    class Media:
        css = {'all': ('forms.css',)}
        js = ('jquery.formvalidation.1.1.5.js',)

# Project editor form for Project Manager Role


class ProjectForm(OpenTaskmanagerModelForm):
    def __init__(self, user, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        user_choices = []
        user_list = Employees
        for item in user_list:
            user_choices.append((item.id, item.name))
        self.fields['users'].choices = user_choices

    name = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Project
        fields = ['name', 'description', 'priority', 'user', 'users']
        localized_fields = ('softdeadline', 'harddeadline',)
        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 20}),
        }
        # the user field is automatically generated depend on logged in user

    class Media:
        css = {'all': ('ui.datepicker.css',)}
        js = ('ui.datepicker.js',)


# Task editor form
class TaskForm(OpenTaskmanagerModelForm):
    def __init__(self, user, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.available_for(user)

    name = forms.CharField(widget=forms.Textarea)
    # project = MyFormField(required=False)
    # parenttask = MyFormField(required=False)

    class Meta:
        model = Task
        fields = (
            'completed',
            'project',
            'parenttask',
            'name',
            'description',
            'owner',
            'assigned_to',
            'tags',
            'priority',
        )
        localized_fields = ('due_date', 'completed_date', 'created_at')
        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 20}),
        }
        # labels, help_texts and error_messages - you can do them for all fields
        labels = {
            'name': _('Task Title'),
        }
        help_texts = {
            'name': _('Enter a short content of the task.'),
        }
        error_messages = {
            'name': {
                'max_length': _("This Task Title is too long."),
            },
        }

    class Media:
        css = {'all': ('ui.datepicker.css',)}
        js = ('ui.datepicker.js',)


CommentForm = modelform_factory(Comment, fields=("text",), widgets={"text": Textarea()})
