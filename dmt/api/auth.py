from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication
from rest_framework import exceptions


class SafeOriginAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        origin = getattr(request.META, 'HTTP_HOST')

        if not origin.endswith('.ccnmtl.columbia.edu'):
            raise exceptions.AuthenticationFailed('Unrecognized origin')

        # Any request using this auth type is considered anonymous
        return (AnonymousUser(), None)
