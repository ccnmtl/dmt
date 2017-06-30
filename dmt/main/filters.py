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
    name = CharFilter(label='Project Name', lookup_expr='icontains')
    projnum = NumberFilter(label='Project Number')
    caretaker_user = ModelChoiceFilter(
        queryset=User.objects.filter(
            ~Q(username__startswith='grp_')).order_by('username'))
    description = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Project
        fields = ['name', 'projnum', 'caretaker_user', 'description']


class UserFilter(FilterSet):
    fullname = CharFilter(label='Full name', lookup_expr='icontains')
    status = ChoiceFilter(choices=[("", "All statuses"),
                                   ("active", "Active"),
                                   ("inactive", "Inactive")])

    class Meta:
        model = User
        fields = ['fullname', 'status']
