from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from rest_framework import exceptions


class CustomJWTCookieAuthentication(JWTCookieAuthentication):
    def authenticate(self, request):
        if request.META.get('IGNORE_TOKEN'):
            return None, None
        return super().authenticate(request)
