import re
from django import forms
from django.forms import ModelForm, TextInput, URLInput
from django_markwhat.templatetags.markup import commonmark
from dmt.main.models import (
    Comment,
    StatusUpdate, Node, UserProfile, Project, Milestone, Item
)
from dmt.main.templatetags.dmttags import linkify


class AddTrackerForm(forms.Form):
    project = forms.ModelChoiceField(queryset=Project.objects.all())
    task = forms.CharField()
    time = forms.CharField()
    client_uni = forms.CharField(required=False)


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
        model = UserProfile
        fields = [
            "fullname", "email", "type", "title", "primary_group",
            "phone", "bio", "photo_url", "campus", "building", "room"
        ]
        widgets = {
            "type": TextInput(),
            "title": TextInput(),
            "phone": TextInput(),
            "photo_url": URLInput(),
            "campus": TextInput(),
            "building": TextInput(),
            "room": TextInput()
        }


class ProjectCreateForm(ModelForm):
    target_date = forms.CharField(label='Proposed release date')

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
    def __init__(self, *args, **kwargs):
        super(ProjectUpdateForm, self).__init__(*args, **kwargs)
        self.fields['caretaker_user'].choices = [
            (user.user.pk, user.fullname) for user in
            self.instance.all_personnel_in_project()]

    class Meta:
        model = Project
        exclude = ['pid']


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
        exclude = ['iid', 'owner', 'owner_user', 'assigned_user',
                   'assigned_to', 'status', 'r_status', 'last_mod',
                   'tags', 'priority', 'url']


class CommentUpdateForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_src']

    def save(self, commit=True):
        instance = super(CommentUpdateForm, self).save(commit=False)
        instance.comment = linkify(commonmark(instance.comment_src))
        if commit:
            instance.save()
        return instance
