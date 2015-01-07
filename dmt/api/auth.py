from rest_framework import permissions
from urlparse import urlparse


class SafeOriginPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        safe_origin = '.columbia.edu'
        origin = request.META.get('REMOTE_HOST')
        referrer = request.META.get('HTTP_REFERER')

        return (origin and origin.endswith(safe_origin)) or \
            (referrer and urlparse(referrer).netloc.endswith(safe_origin))
