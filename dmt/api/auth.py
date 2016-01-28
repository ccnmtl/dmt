from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication
from rest_framework import permissions
from urlparse import urlparse


class SafeOriginAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        return (AnonymousUser(), None)


class SafeOriginPermission(permissions.BasePermission):
    """URL and IP whitelist permissions.

    Put settings like this in your local_settings.py:

    WHITELIST_ORIGIN_IPS = (
        '128.59.222.80',  # selma.ccnmtl.columbia.edu
    )

    WHITELIST_ORIGIN_URLS = (
        '.columbia.edu',
    )
    """

    def _has_safe_remote_addr(self, remote_addr):
        try:
            return settings.WHITELIST_ORIGIN_IPS and \
                (remote_addr in settings.WHITELIST_ORIGIN_IPS)
        except AttributeError:
            return False

    def _has_safe_referrer(self, referrer):
        try:
            # .endswith checks each element of the WHITELIST_ORIGIN_URLS
            # tuple
            return referrer and \
                urlparse(referrer).netloc.endswith(
                    settings.WHITELIST_ORIGIN_URLS)
        except AttributeError:
            return False

    def _has_safe_remote_host(self, remote_host):
        try:
            return remote_host and remote_host.endswith(
                settings.WHITELIST_ORIGIN_URLS)
        except AttributeError:
            return False

    def has_permission(self, request, view):
        real_ip = request.META.get('HTTP_X_REAL_IP')
        remote_addr = request.META.get('REMOTE_ADDR')
        remote_host = request.META.get('REMOTE_HOST')
        referrer = request.META.get('HTTP_REFERER')

        checks = [
            self._has_safe_remote_addr(real_ip),
            self._has_safe_remote_addr(remote_addr),
            self._has_safe_remote_host(remote_host),
            self._has_safe_referrer(referrer),
        ]

        # Return True if any of the checks are True
        return any(checks)
