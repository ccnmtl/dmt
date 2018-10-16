from django.contrib.auth.models import User
from django.db.models import Q
from django_filters import (
    CharFilter, FilterSet, ModelChoiceFilter, NumberFilter,
    ChoiceFilter,
)

from .models import Client, Project


class ClientFilter(FilterSet):
    lastname = CharFilter(label='Last Name', lookup_expr='icontains')
    firstname = CharFilter(label='First Name', lookup_expr='icontains')
    department = CharFilter(lookup_expr='icontains')
    school = CharFilter(lookup_expr='icontains')
    email = CharFilter(lookup_expr='icontains')
    phone = CharFilter(label='Phone Number', lookup_expr='icontains')
    comments = CharFilter(lookup_expr='icontains')
    user = ModelChoiceFilter(
        queryset=User.objects.filter(
            ~Q(username__startswith='grp_')
        ).order_by('username'))

    class Meta:
        model = Client
        fields = ['lastname', 'firstname', 'department', 'school', 'email',
                  'phone', 'comments', 'user']


class ProjectFilter(FilterSet):
    class Meta:
        model = Project
        fields = ['name', 'status', 'projnum', 'caretaker_user',
                  'project_manager_user', 'description']

    name = CharFilter(label='Project Name', lookup_expr='icontains')
    projnum = NumberFilter(label='Project Number')
    caretaker_user = ModelChoiceFilter(
        queryset=User.objects.filter(
            ~Q(username__startswith='grp_')).order_by('username'))
    project_manager_user = ModelChoiceFilter(
        queryset=User.objects.filter(
            ~Q(username__startswith='grp_')).order_by('username'))
    description = CharFilter(lookup_expr='icontains')

    @property
    def qs(self):
        parent = super(ProjectFilter, self).qs
        s = self.data.get('status')

        # If the user is looking for a Defunct or Archived project,
        # don't ignore them from the query.
        if s == 'Defunct' or s == 'Archived':
            return parent.filter(pub_view=True)
        else:
            # Defunct and Archived are ignored by default.
            return parent.exclude(
                Q(status='Defunct') | Q(status='Archived')
            ).filter(pub_view=True)


class UserFilter(FilterSet):
    fullname = CharFilter(label='Full name', lookup_expr='icontains')
    status = ChoiceFilter(choices=[("", "All statuses"),
                                   ("active", "Active"),
                                   ("inactive", "Inactive")])

    class Meta:
        model = User
        fields = ['fullname', 'status']
