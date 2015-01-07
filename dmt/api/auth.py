from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework import permissions


class IsAnonymous(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_anonymous()


class SafeOriginAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        origin = request.META.get('REMOTE_HOST')

        if not origin.endswith('.columbia.edu'):
            raise exceptions.AuthenticationFailed('Unrecognized origin')

        # Any request using this auth type is considered anonymous
        return (AnonymousUser(), None)
