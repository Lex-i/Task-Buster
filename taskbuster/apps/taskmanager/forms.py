# from django.forms import ModelForm, Textarea, modelform_factory
from django import forms
# from django.contrib.auth.models import User as auser
from taskmanager.models import *
# from taskmanager.templatetags.extras import username
from django.utils.translation import gettext_lazy as _


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
    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_list = Employee.objects.all().order_by('name')
        self.fields["project"] = forms.IntegerField(widget=forms.HiddenInput(), initial=project_id)
        # self.fields["employee"] = forms.ModelMultipleChoiceField(
        self.fields["employee"] = forms.ModelChoiceField(
            queryset=user_list,
            # to_field_name="name",
            # required=False,
            # widget=forms.SelectMultiple(),
            # choices=user_choices,
            # label=_("Project Team")
        )

    class Meta:
        model = ProjectTeam
        fields = ('project', 'employee',)
        # the user field is automatically generated depend on logged in user

    class Media:
        css = {'all': ('css/bootstrap.min.css',
                       'css/bootstrap-theme.min.css',
                       'css/main.css')}
        js = ('js/vendor/modernizr-2.8.3-respond-1.4.2.min.js',
              'js/plugins.js',
              'js/vendor/bootstrap.js',
              'js/vendor/bootstrap.min.js',
              'js/vendor/jquery-1.11.2.js',
              )


TeamFormSet = forms.inlineformset_factory(
    Project,
    ProjectTeam,
    fk_name='project',
    fields=('employee',),
    extra=Employee.objects.count() - 1
)


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        user_list = Employee.objects.all().order_by('name')
        # ProjectTeam
        # user_choices = [(item.id, item.name) for item in user_list]
        # self.fields['users'].choices = user_choices
        # self.fields['user'].choices = user_choices
        self.fields["user"] = forms.ModelChoiceField(
            queryset=user_list,
            # widget=forms.Select(),
            # choices=user_choices,
            # initial=auser.employee,
        )  # initial=User.employee)
        # self.fields["users"] = forms.ModelMultipleChoiceField(
        # queryset=user_list,
        # required=False,
        # widget=forms.SelectMultiple(),
        # choices=user_list,
        # label=_("Project Team")
        # )
        # self.fields['users'].
        # self.fields['user'].queryset = (Employee.objects.all().order_by('name'))

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
        fields = ('name', 'description', 'priority', 'user', 'users')
        localized_fields = ('softdeadline', 'harddeadline',)
        # the user field is automatically generated depend on logged in user

    class Media:
        css = {'all': ('css/bootstrap.min.css',
                       'css/bootstrap-theme.min.css',
                       'css/main.css')}
        js = ('js/vendor/modernizr-2.8.3-respond-1.4.2.min.js',
              'js/plugins.js',
              'js/vendor/bootstrap.js',
              'js/vendor/bootstrap.min.js',
              'js/vendor/jquery-1.11.2.js',
              )


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
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
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


CommentForm = forms.modelform_factory(Comment, fields=("text",), widgets={"text": forms.Textarea()})
