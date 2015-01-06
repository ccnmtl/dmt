from django.db.models import Q
from django_filters import (
    CharFilter, FilterSet, ModelChoiceFilter, NumberFilter
)

from dmt.main.models import UserProfile


class ClientFilter(FilterSet):
    lastname = CharFilter(label='Last Name', lookup_type='icontains')
    firstname = CharFilter(label='First Name', lookup_type='icontains')
    department = CharFilter(lookup_type='icontains')
    school = CharFilter(lookup_type='icontains')
    email = CharFilter(lookup_type='icontains')
    phone = CharFilter(label='Phone Number', lookup_type='icontains')
    comments = CharFilter(lookup_type='icontains')
    contact = ModelChoiceFilter(
        queryset=UserProfile.objects.filter(
            Q(status__iexact='active') & ~Q(username__startswith='grp_')
        ))


class ProjectFilter(FilterSet):
    name = CharFilter(label='Project Name', lookup_type='icontains')
    projnum = NumberFilter(label='Project Number')
    caretaker = ModelChoiceFilter(
        queryset=UserProfile.objects.filter(
            Q(status__iexact='active') & ~Q(username__startswith='grp_')
        ))
    description = CharFilter(lookup_type='icontains')


class UserFilter(FilterSet):
    username = CharFilter(lookup_type='icontains')
    fullname = CharFilter(label='Full Name', lookup_type='icontains')
    email = CharFilter(lookup_type='icontains')
    phone = CharFilter(label='Phone Number', lookup_type='icontains')
    title = CharFilter(lookup_type='icontains')
    bio = CharFilter(lookup_type='icontains')
