# from django.forms import ModelForm, Textarea, modelform_factory
from django import forms
# from django.contrib.auth.models import User as auser
from taskmanager.models import *
# from taskmanager.templatetags.extras import username
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.forms import AuthenticationForm


class AuthenticationFormWithInactiveUsersOkay(AuthenticationForm):
    def confirm_login_allowed(self, user):
        pass


class OpenTaskmanagerModelForm(forms.ModelForm):
    class Media:
        css = {'all': ('forms.css',)}
        js = ('jquery.formvalidation.1.1.5.js',)

# Project editor form for Project Manager Role


class CalendarWidget(forms.TextInput):
    class Media:
        css = {'all': ('css/cal.css',)}
        js = ('js/cal.js',)


class TeamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_list = Employee.objects.all().order_by('name')
        self.fields["employee"] = forms.ModelChoiceField(
            queryset=user_list,
            widget=forms.Select(
                attrs={
                    'class': 'custom-select d-block w-100',
                }
            )
        )

    class Meta:
        model = ProjectTeam
        fields = ('employee',)
        widgets = {
            'employee': forms.Select(
                attrs={'class': 'custom-select d-block w-100', }),
            "DELETE": forms.CheckboxInput(attrs={'class': 'container1'})
        }

    class Media:
        css = {'all': ('css/bootstrap.min.css',
                       'css/bootstrap-theme.min.css',
                       'css/main.css')}


class TeamForm1(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_list = Employee.objects.all().order_by('name')
        self.fields["employee"] = forms.ModelMultipleChoiceField(
            queryset=user_list,
        )

    class Meta:
        model = ProjectTeam
        fields = ("employee",)
        widgets = {'employee': forms.SelectMultiple()}

    # class Media:
    #     css = {'all': ('css/bootstrap.min.css',
    #                    'css/bootstrap-theme.min.css',
    #                    'css/main.css')}
    #     js = ('js/vendor/modernizr-2.8.3-respond-1.4.2.min.js',
    #           'js/plugins.js',
    #           'js/vendor/bootstrap.js',
    #           'js/vendor/bootstrap.min.js',
    #           'js/vendor/jquery-1.11.2.js',
    #           )


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        user_list = Employee.objects.all().order_by('name')
        self.fields["user"] = forms.ModelChoiceField(
            queryset=user_list,
            widget=forms.Select(
                attrs={
                    'class': 'custom-select d-block w-100',
                    # 'style':'',
                    'placeholder': _("Choose manager")
                })
        )
        self.fields["name"] = forms.CharField(
            required=True,
            max_length=128,
            widget=forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': _("Enter the project title")
                },
            ),
            help_text=_("Please enter the project title."),
        )
        self.fields["description"] = forms.CharField(
            widget=forms.Textarea(
                attrs={
                    'rows': 5,
                    'class': 'form-control',
                    'placeholder': _("Enter the project description")
                }
            )
        )
        self.fields["priority"] = forms.IntegerField(
            initial=1,
            widget=forms.NumberInput(
                attrs={
                    'class': 'form-control',
                }
            )
        )
        self.fields["softdeadline"] = forms.DateField(
            localize=True,
            widget=forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            )
        )
        self.fields["harddeadline"] = forms.DateField(
            localize=True,
            widget=forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            )
        )

    class Meta:
        model = Project
        fields = ('name', 'description', 'priority', 'user',)
        localized_fields = ('softdeadline', 'harddeadline',)
        # the user field is automatically generated depend on logged in user

    # class Media:
    #     css = {'all': ('css/bootstrap.min.css',
    #                    'css/bootstrap-theme.min.css',
    #                    'css/main.css')}
    #     js = ('js/vendor/modernizr-2.8.3-respond-1.4.2.min.js',
    #           'js/plugins.js',
    #           'js/vendor/bootstrap.js',
    #           'js/vendor/bootstrap.min.js',
    #           'js/vendor/jquery-1.11.2.js',
    #           )


class BaseProjectFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


ProjectFormSet = forms.modelformset_factory(
    Project,
    fields=('name', 'description', 'priority', 'user'),
    localized_fields=('softdeadline', 'harddeadline',),
    # exclude=(),
    form=ProjectForm,
)


# Task editor form
class TaskForm(forms.ModelForm):
    def __init__(self, user, project, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        user_list = Employee.objects.all().order_by('name')
        task_list = project.related_tasks.all().order_by('due_date')
        # self.fields['project'].queryset = Project.objects.available_for(user)

        # self.fields["owner"] = forms.ModelChoiceField(
        #     queryset=user_list,
        #     widget=forms.Select(
        #         attrs={
        #             'class': 'custom-select d-block w-100',
        #             # 'style':'',
        #             'placeholder': _("Choose owner"),
        #             # 'disabled': 'disabled',
        #             # 'value': instance.owner,
        #         })
        # )
        self.fields["assigned_to"] = forms.ModelChoiceField(
            queryset=user_list,
            widget=forms.Select(
                attrs={
                    'class': 'custom-select d-block w-100',
                    # 'style':'',
                    'placeholder': _("Choose assignee")
                })
        )

        self.fields["parenttask"] = forms.ModelChoiceField(
            required=False,
            queryset=task_list,
            widget=forms.Select(
                attrs={
                    'class': 'custom-select d-block w-100',
                    # 'style':'',
                    'placeholder': _("Choose parrent task")
                })
        )

        self.fields["name"] = forms.CharField(
            required=True,
            max_length=128,
            widget=forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': _("Enter the task title")
                },
            ),
            help_text=_("Please enter the project title."),
        )
        self.fields["description"] = forms.CharField(
            widget=forms.Textarea(
                attrs={
                    'rows': 5,
                    'class': 'form-control',
                    'placeholder': _("Enter the task description")
                }
            )
        )
        self.fields["priority"] = forms.IntegerField(
            initial=1,
            widget=forms.NumberInput(
                attrs={
                    'class': 'form-control',
                }
            )
        )
        self.fields["due_date"] = forms.DateField(
            localize=True,
            widget=forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            )
        )
        self.fields["completed"] = forms.BooleanField(
            required=False,
            initial=False,
            widget=forms.CheckboxInput(
                attrs={
                    'class': 'form-control',
                }
            )
        )

    class Meta:
        model = Task
        fields = [
            'completed',
            'project',
            'parenttask',
            'name',
            'description',
            # 'owner',
            'assigned_to',
            # 'tags',
            'priority',
            'due_date'
        ]
        localized_fields = ('due_date',)

        # labels, help_texts and error_messages: you can do them for all fields
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

    # class Media:
    #     css = {'all': ('css/bootstrap.min.css',
    #                    'css/bootstrap-theme.min.css',
    #                    'css/main.css')}
    #     js = ('js/vendor/modernizr-2.8.3-respond-1.4.2.min.js',
    #           'js/plugins.js',
    #           'js/vendor/bootstrap.js',
    #           'js/vendor/bootstrap.min.js',
    #           'js/vendor/jquery-1.11.2.js',
    #           )


class TaskForm1(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'completed',
            'project',
            'parenttask',
            'name',
            'description',
            # 'owner',
            # 'assigned_to',
            # 'tags',
            'priority'
        ]


CommentForm = forms.modelform_factory(Comment, fields=(
    "text",), widgets={"text": forms.Textarea()})
