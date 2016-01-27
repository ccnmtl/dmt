import re
from datetime import timedelta
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models.functions import Lower
from django.forms import ModelForm, TextInput, URLInput
from django_markwhat.templatetags.markup import commonmark
from extra_views import InlineFormSet
from simpleduration import Duration, InvalidDuration
from dmt.main.models import (
    Comment,
    StatusUpdate, Node, UserProfile, Project, Milestone, Item,
    Reminder
)
from dmt.main.templatetags.dmttags import linkify
from dmt.main.utils import simpleduration_string


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


class ProjectPersonnelForm(forms.Form):
    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }

    def __init__(self, *args, **kwargs):
        pid = kwargs.pop('pid')
        r = super(ProjectPersonnelForm, self).__init__(*args, **kwargs)
        p = Project.objects.get(pk=pid)
        qs = UserProfile.objects.filter(
            pk__in=[u.pk for u in p.all_users_not_in_project()]
        ).order_by(Lower('fullname')).order_by(Lower('username'))
        self.fields['personnel'] = forms.ModelMultipleChoiceField(
            queryset=qs,
            widget=FilteredSelectMultiple('Personnel', is_stacked=False),
            label='')
        return r


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


class SimpleDurationField(forms.DurationField):
    def prepare_value(self, value):
        return simpleduration_string(value)

    def clean(self, value):
        try:
            d = Duration(value).timedelta()
        except InvalidDuration:
            d = timedelta(hours=1)

        return super(SimpleDurationField, self).clean(d)


class ReminderForm(ModelForm):
    class Meta:
        model = Reminder
        exclude = ['user']

    reminder_time = SimpleDurationField(
        help_text='Enter time and unit. For example: <code>1d</code> ' +
        'to be reminded one day before the target date. The minimum ' +
        'granularity for reminders is hourly.')


class RemindersInlineFormSet(InlineFormSet):
    model = Reminder
    form_class = ReminderForm
    min_num = 1
    max_num = 1


class ItemUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ItemUpdateForm, self).__init__(*args, **kwargs)
        passed_item = kwargs.get('instance')
        milestone = Milestone.objects.get(item=passed_item)
        project = Project.objects.get(milestone=milestone)
        project_milestones = project.milestone_set.all()
        self.fields['milestone'].queryset = project_milestones
        self.fields['estimated_time'] = SimpleDurationField(
            help_text='Enter time and unit. For example: <code>2h 30m</code>',
            initial='1h')

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
