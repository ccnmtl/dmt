from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication
from rest_framework import permissions
from urlparse import urlparse


class SafeOriginAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        return (AnonymousUser(), None)


class SafeOriginPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        safe_origin = '.columbia.edu'
        origin = request.META.get('REMOTE_HOST')
        referrer = request.META.get('HTTP_REFERER')

        return (origin and origin.endswith(safe_origin)) or \
            (referrer and urlparse(referrer).netloc.endswith(safe_origin))
