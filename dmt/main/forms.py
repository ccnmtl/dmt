import re
from django import forms
from django.forms import ModelForm
from .models import StatusUpdate, Node, User, Project, Milestone, Item


class StatusUpdateForm(ModelForm):
    class Meta:
        model = StatusUpdate
        fields = ['body']


class NodeUpdateForm(ModelForm):
    class Meta:
        model = Node
        fields = ['subject', 'body']


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ["fullname", "email", "type", "title", "phone",
                  "bio", "photo_url", "photo_width", "photo_height",
                  "campus", "building", "room"]


class ProjectCreateForm(ModelForm):
    target_date = forms.CharField(label='Final release date')

    class Meta:
        model = Project
        fields = ['name', 'description', 'pub_view', 'target_date',
                  'wiki_category']
        widgets = {
            'pub_view': forms.RadioSelect(
                choices=(('true', 'Public'),
                         ('false', 'Private')))
        }

    def clean_name(self):
        return self.cleaned_data.get('name', '').strip()

    def clean_target_date(self):
        target_date = self.cleaned_data.get('target_date')
        if not re.match(r'\d{4}-\d{1,2}-\d{1,2}', target_date):
            raise forms.ValidationError(
                'Invalid target date: %s' % target_date)


class ProjectUpdateForm(ModelForm):
    class Meta:
        model = Project
        exclude = ['pid', ]


class MilestoneUpdateForm(ModelForm):
    class Meta:
        model = Milestone
        exclude = ['mid', 'project', 'status']


class ItemUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ItemUpdateForm, self).__init__(*args, **kwargs)
        passed_item = kwargs.get('instance')
        milestone = Milestone.objects.get(item=passed_item)
        project = Project.objects.get(milestone=milestone)
        project_milestones = project.milestone_set.all()
        self.fields['milestone'].queryset = project_milestones

    class Meta:
        model = Item
        exclude = ['iid', 'owner',
                   'assigned_to', 'status', 'r_status', 'last_mod',
                   'tags', 'priority']
