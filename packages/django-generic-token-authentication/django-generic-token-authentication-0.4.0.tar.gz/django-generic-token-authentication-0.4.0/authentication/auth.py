from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from utility.functions import get_current_datetime


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:
    Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """
    keyword = 'Token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from authentication.models import AuthToken
        return AuthToken

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        model = self.get_model()
        model.objects.filter(created__lte=get_current_datetime() - settings.REFRESH_TOKEN_EXPIRY).delete()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = """Invalid token header. Token string should not contain 
                     invalid characters."""
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token, request)

    def authenticate_credentials(self, key, request):
        model = self.get_model()

        try:
            token = model.objects.get(id=key[:32])
        except ObjectDoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if check_password(key[32:], token.key):
            if not token.user.is_active:
                raise exceptions.AuthenticationFailed('User inactive or deleted.')
            if (token.created < (get_current_datetime()
                                 - settings.TOKEN_EXPIRY)
                    and "refresh" not in request.META['PATH_INFO']):
                raise exceptions.AuthenticationFailed("""Token has expired.
                                                      Please refresh token.""")
            else:
                return token.user, key

        raise exceptions.AuthenticationFailed('Invalid token.')

    def authenticate_header(self, request):
        return self.keyword
