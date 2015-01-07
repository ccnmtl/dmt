from rest_framework import permissions


class SafeOriginPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        origin = request.META.get('REMOTE_HOST')
        return (origin and origin.endswith('.columbia.edu'))
