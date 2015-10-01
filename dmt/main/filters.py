from django.contrib.auth.models import User
from django.db.models import Q
from django_filters import (
    CharFilter, FilterSet, ModelChoiceFilter, NumberFilter,
    ChoiceFilter,
)


class ClientFilter(FilterSet):
    lastname = CharFilter(label='Last Name', lookup_type='icontains')
    firstname = CharFilter(label='First Name', lookup_type='icontains')
    department = CharFilter(lookup_type='icontains')
    school = CharFilter(lookup_type='icontains')
    email = CharFilter(lookup_type='icontains')
    phone = CharFilter(label='Phone Number', lookup_type='icontains')
    comments = CharFilter(lookup_type='icontains')
    user = ModelChoiceFilter(
        queryset=User.objects.filter(
            ~Q(username__startswith='grp_')
        ))


class ProjectFilter(FilterSet):
    name = CharFilter(label='Project Name', lookup_type='icontains')
    projnum = NumberFilter(label='Project Number')
    caretaker_user = ModelChoiceFilter(
        queryset=User.objects.filter(~Q(username__startswith='grp_')))
    description = CharFilter(lookup_type='icontains')


class UserFilter(FilterSet):
    fullname = CharFilter(label='Full name', lookup_type='icontains')
    status = ChoiceFilter(choices=[("", "All statuses"),
                                   ("active", "Active"),
                                   ("inactive", "Inactive")])
