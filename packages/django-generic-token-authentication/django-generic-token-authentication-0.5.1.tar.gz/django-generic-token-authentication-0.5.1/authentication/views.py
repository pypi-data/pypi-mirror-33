import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from generic.factories import generic_factory
from generic.repositories import GenericRepository
from generic.services import (generic_retrieve_single_service,
                              generic_delete_service,
                              generic_update_service,
                              generic_create_service)
from generic.validators import validate_many, is_value_unique
from generic.views import GenericViewset
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utility.exceptions import (ValidationError,
                                ObjectNotFoundError,
                                InternalError)
from utility.functions import get_current_datetime
from utility.logger import get_log_msg

from authentication.repositories import (TokenRepository,
                                         ResetRepository,
                                         MailVerificationRepository)
from authentication.serializers import (UserSerializer,
                                        RegisterSerializer,
                                        UpdatePasswordSerializer,
                                        RefreshSerializer,
                                        ResetSerializer,
                                        ConfirmSerializer)
from authentication.services import (retrieve_token_service,
                                     logout_service,
                                     logout_all_service,
                                     refresh_token_service,
                                     reset_password_service,
                                     validate_reset_password_service,
                                     confirm_reset_password_service,
                                     validate_email_service,
                                     confirm_email_service)
from authentication.validators import (is_email_valid,
                                       is_password_length_sufficient,
                                       does_contain_char_classes)

User = get_user_model()
LOGGER = logging.getLogger("views")


# noinspection PyUnusedLocal
class PasswordRequirementsView(APIView):
    """
    PasswordRequirementsView

    Returns the password requirements.

    **Parameters and return value**

    :allowed: GET
    :auth required: False
    :many: False
    :returns: 200 in case of success
    :returns: json object containing the password requirements
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/password.json' \
        --header 'Content-Type: application/json'

    **Return value example of GET request**

    {
    
        "minimalLength": 12,
    
        "charClasses": 3
    
    }
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        user = self.request.user
        LOGGER.info(get_log_msg(self.request, user))
        content = {'minimalLength': settings.MIN_PASSWORD_LENGTH,
                   'charClasses': settings.CHAR_CLASSES}

        return Response(content, status=status.HTTP_200_OK)


# noinspection PyUnusedLocal
class UserViewSet(viewsets.ViewSet):
    """
    UserViewSet

    Provides get, update and delete operations for
    :model:`authentication.User` instances.

    **Parameters and return value**

    :allowed: GET, PATCH, DELETE
    :auth required: True
    :many: False
    :returns: 200 in case of success
    :error: 400 if a validation error occurs (inspect response for details)
    :error: 401 if the request is unauthorized
    :error: 404 if the requested user could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/users/d47947b4-65b1.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb11e423374d' \
        --header 'Content-Type: application/json'

    **Return value example of GET request**
    {

        "id": "a9caebca-5a81-11e8-8a23-f40f2434c1ce",

        "username": "josefK1526637368",

        "email": "josefK1526637368@example.com",

        "firstName": "Josef",

        "lastName": "K"

    }
    """
    repository = GenericRepository(User)
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None, format=None):
        """
        Builds and exposes retrieve view for users
        """
        service = generic_retrieve_single_service(self.repository)
        view = GenericViewset(self.serializer_class, service, request)

        return view.retrieve(pk)

    def destroy(self, request, pk=None, format=None):
        """
        Builds and exposes destroy view for users
        """
        service = generic_delete_service(self.repository)
        view = GenericViewset(self.serializer_class, service, request)

        return view.destroy(pk)

    def partial_update(self, request, pk=None, format=None):
        """
        Builds and exposes partial update view for users
        """
        validators = (is_email_valid(self.repository),
                      is_value_unique(self.repository, 'email'),
                      is_value_unique(self.repository, 'username'))
        service = generic_update_service(self.repository, validate_many(*validators))
        view = GenericViewset(self.serializer_class, service, request)

        return view.partial_update(pk)


# noinspection PyUnusedLocal
class UpdatePasswordViewSet(viewsets.ViewSet):
    """
    UpdatePasswordViewSet

    Provides update password operation for
    :model:`authentication.User` instances.

    **Parameters and return value**

    :allowed: PATCH
    :auth required: True
    :many: False
    :returns: 204 in case of success
    :error: 400 if a validation error occurs (inspect response for details)
    :error: 401 if the request is unauthorized
    :error: 404 if the requested user could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for PATCH request**

    curl --request PATCH \
        --url 'https://api.basement.technology/auth/users/d47947b4-65b1.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb11e423374d' \
        --header 'Content-Type: application/json'
        --data

        '{

            "password1": "new_password",

            "password2": "new_password"

        }'
    """
    repository = GenericRepository(User)
    serializer_class = UpdatePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def partial_update(self, request, pk=None, format=None):
        """
        Builds and exposes update password view for users
        """
        validators = (is_password_length_sufficient(self.repository, settings.MIN_PASSWORD_LENGTH),
                      does_contain_char_classes(self.repository, settings.CHAR_CLASSES))
        service = generic_update_service(self.repository, validate_many(*validators))

        view = GenericViewset(self.serializer_class, service, request)
        response = view.partial_update(pk)

        if response.status_code == 200:
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        return response


# noinspection PyUnusedLocal
class RegisterViewSet(viewsets.ViewSet):
    """
    RegisterViewSet

    Provides create operation for :model:`authentication.User` instances.

    **Parameters and return value**

    :allowed: POST
    :auth required: False
    :many: False
    :returns: 201 in case of success
    :returns: user instance that was created
    :error: 400 if posted user object is invalid: json representation 
                is invalid, password is too weak, email address is invalid
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for POST request**

    curl --request POST \
        --url https://api.basement.technology/auth/token.json \
        --header 'Content-Type: application/json' \
        --data

        '{

            "username": "josef1526637489",

            "password": "1Secure#Password"

        }'

    **Return value example of POST request**
    {

        "id": "f7c8aaa6-5a81-11e8-bd41-f40f2434c1ce",

        "username": "josef1526637489",

        "email": null,

        "firstName": null,

        "lastName": null

    }
    """
    repository = GenericRepository(User)
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def create(self, request, format=None):
        """
        Builds and exposes create view for users
        """
        validators = (is_email_valid(self.repository),
                      is_value_unique(self.repository, 'id'),
                      is_value_unique(self.repository, 'email'),
                      is_value_unique(self.repository, 'username'),
                      is_password_length_sufficient(self.repository, settings.MIN_PASSWORD_LENGTH),
                      does_contain_char_classes(self.repository, settings.CHAR_CLASSES))
        service = generic_create_service(self.repository, validate_many(*validators), generic_factory)

        view = GenericViewset(self.serializer_class, service, request)
        response = view.create()

        if 'password' in response.data:
            del response.data['password']

        return response


# noinspection PyUnusedLocal
class TokenViewSet(viewsets.ViewSet):
    """
    TokenView

    Provides api endpoint that delivers api access tokens.
    Takes username and password of :model:`authentication.User` instance.

    **Parameters and return value**

    :allowed: POST
    :auth required: False
    :many: False
    :returns: 200 in case of success
    :returns: token and refresh token with expiry time
    :error: 400 if posted credentials are invalid
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for POST request**

    curl --request POST \
        --url https://api.basement.technology/auth/token.json \
        --header 'Content-Type: application/json' \
        --data

        '{

            "username": "johndoe@example.com",

            "password": "John-Doe-1"

        }'

    **Return value example of POST request**

    {

        "userId": "babda7de-6115-11e8-add9-f40f2434c1ce",

        "token": "x8bxmnsaxniz9q800h8pm554efj4l7b2u921d1c0ld66w3rf9t0rirc",

        "refreshToken": "th7t047ag6bnwkurqd9e81a9630ssuhuermh7qeb7vew8wan",

        "tokenExpiry": "2018-05-26T20:00:15.563893Z",

        "refreshTokenExpiry": "2018-05-27T19:00:15.563915Z"
        
    }
    """
    permission_classes = (AllowAny,)
    serializer_class = AuthTokenSerializer
    repository = TokenRepository()

    def create(self, request, format=None):
        """
        Takes a user's username and password and generates a new token for
        that user if username and password are correct
        """
        data = request.data
        serializer = self.serializer_class(data=data,
                                           context={'request': request})

        if serializer.is_valid(raise_exception=False):
            user = serializer.validated_data['user']
            LOGGER.info(get_log_msg(self.request, user))
            return self._retrieve_token(request, user)

        LOGGER.info(get_log_msg(self.request, self.request.user))
        return self._handle_error('Validation failed.', status.HTTP_400_BAD_REQUEST)

    def _retrieve_token(self, request, user):
        service = retrieve_token_service(self.repository)
        (token, refresh_token) = service(user)
        exp = get_current_datetime() + settings.TOKEN_EXPIRY
        refresh_exp = get_current_datetime() + settings.REFRESH_TOKEN_EXPIRY
        content = {'userId': user.id,
                   'token': token,
                   'refreshToken': refresh_token,
                   'tokenExpiry': exp,
                   'refreshTokenExpiry': refresh_exp}
        user_logged_in.send(sender=user.__class__, request=request, user=user)

        return Response(content, status=status.HTTP_200_OK)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: e}
        return Response(content, status=status_code)


# noinspection PyUnusedLocal
class LogoutViewSet(viewsets.ViewSet):
    """
    LogoutViewSet

    Provides api endpoint that deletes the token that is passed by header.

    **Parameters and return value**

    :allowed: GET
    :auth required: True
    :many: False
    :returns: 204 in case of success
    :error: 400 if the request is malformed, should never happen
    :error: 404 if the passed token could not be found, should never happen
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/logout.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471' \
        --header 'Content-Type: application/json'
    """
    repository = TokenRepository()

    def list(self, request, format=None):
        """
        Destroys the token that was used got authentication
        """
        if 'HTTP_AUTHORIZATION' not in request.META:
            return self._handle_error('No auth header provided.', status.HTTP_401_UNAUTHORIZED)

        service = logout_service(self.repository)
        token_str = str(request.META['HTTP_AUTHORIZATION'])
        token = token_str.split(sep=' ', maxsplit=1)[1]
        try:
            service(token)
        except ObjectNotFoundError as e:
            return self._handle_error(e, status.HTTP_401_UNAUTHORIZED)
        except ValidationError as e:
            return self._handle_error(e, status.HTTP_401_UNAUTHORIZED)

        user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


# noinspection PyUnusedLocal
class LogoutAllViewSet(viewsets.ViewSet):
    """
    LogoutViewSet

    Provides api endpoint that deletes all tokens of the logged in user.

    **Parameters and return value**

    :allowed: GET
    :auth required: True
    :many: False
    :returns: 204 in case of success
    :error: 400 if the request is malformed, should never happen
    :error: 401 if the request is unauthorized
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/logoutall.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb' \
        --header 'Content-Type: application/json'
    """
    repository = TokenRepository()

    def list(self, request, format=None):
        """
        Destroys all tokens associated with the authenticated user
        """
        if 'HTTP_AUTHORIZATION' not in request.META:
            return self._handle_error('No auth header provided.', status.HTTP_401_UNAUTHORIZED)

        service = logout_all_service(self.repository)
        service(request.user)
        user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


# noinspection PyUnusedLocal
class RefreshViewSet(viewsets.ViewSet):
    """
    RefreshViewSet

    Provides api endpoint that refreshes api access tokens.
    Takes token and refresh token of :model:`authentication.AuthToken` instance.

    **Parameters and return value**

    :allowed: POST
    :auth required: True
    :many: False
    :returns: 200 in case of success
    :returns: token and refresh token with expiry times (see example below)
    :error: 400 if posted json object is invalid
    :error: 401 if the request is unauthorized
    :error: 404 if posted token could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for POST request**

    curl --request POST \
        --url 'https://api.basement.technology/auth/refresh.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb' \
        --header 'Content-Type: application/json' \
        --data

        '{

            "refreshToken": "1a958a16e9ab03489f8aa345851248d23062f9"

        }'


    **Return value example of POST request**

    {

        "userId": "babda7de-6115-11e8-add9-f40f2434c1ce",

        "token": "x8bxmnsaxniz9q800h8pm554efj4l7b2u",

        "refreshToken": "2r17z2hedt2hsjjp79g97hxyzoyuy4dw2cq",

        "tokenExpiry": "2018-05-26T20:00:15.563893Z",

        "refreshTokenExpiry": "2018-05-27T19:00:15.563915Z"

    }
    """
    serializer_class = RefreshSerializer
    repository = TokenRepository()

    def create(self, request, format=None):
        """
        Takes a user's refresh token and generates a new token for
        that user
        """
        if 'HTTP_AUTHORIZATION' not in request.META:
            return self._handle_error('No auth header provided.', status.HTTP_401_UNAUTHORIZED)

        data = request.data
        serializer = self.serializer_class(data=data, context={'request': request})

        if serializer.is_valid(raise_exception=False):
            token_str = str(request.META['HTTP_AUTHORIZATION'])
            token = token_str.split(sep=' ', maxsplit=1)[1]
            refresh_token = serializer.validated_data['refreshToken']
            LOGGER.info(get_log_msg(self.request, request.user))
            return self._refresh_token(request.user, token, refresh_token)

        LOGGER.info(get_log_msg(self.request, self.request.user))

        return self._handle_error("Validation failed.", status.HTTP_400_BAD_REQUEST)

    def _refresh_token(self, user, token, refresh_token):
        service = refresh_token_service(self.repository)

        try:
            (token, refresh_token) = service(user, token, refresh_token)
        except ObjectNotFoundError as e:
            return self._handle_error(e, status.HTTP_401_UNAUTHORIZED)
        except ValidationError as e:
            return self._handle_error(e, status.HTTP_401_UNAUTHORIZED)

        exp = get_current_datetime() + settings.TOKEN_EXPIRY
        refresh_exp = get_current_datetime() + settings.REFRESH_TOKEN_EXPIRY
        content = {'userId': user.id,
                   'token': token,
                   'refreshToken': refresh_token,
                   'tokenExpiry': exp,
                   'refreshTokenExpiry': refresh_exp}

        return Response(content, status=status.HTTP_200_OK)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


# noinspection PyUnusedLocal
class ResetPasswordViewSet(viewsets.ViewSet):
    """
    ResetPasswordViewSet

    Provides api endpoint that resets a users' password.
    Takes email address of :model:`authentication.AuthToken` instance.

    **Parameters and return value**

    :allowed: POST
    :auth required: False
    :many: False
    :returns: 204 in case of success
    :returns: only status code is returned, also sends an email to the
              given address
    :error: 400 if posted json object is invalid or if the email address 
                has not been verified
    :error: 404 if posted user could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for POST request**

    curl --request POST \
        --url 'https://api.basement.technology/auth/resetpassword.json' \
        --header 'Content-Type: application/json' \
        --data

        '{

            "email": "john.doe@example.com"

        }'
    """
    serializer_class = ResetSerializer
    repository = ResetRepository()
    permission_classes = (AllowAny,)

    def create(self, request, format=None):
        """
        Sends reset password email to the posted email address
        """
        data = request.data
        serializer = self.serializer_class(data=data,
                                           context={'request': request})

        if serializer.is_valid(raise_exception=False):
            email = serializer.validated_data['email']
            LOGGER.info(get_log_msg(self.request, request.user))
            return self._reset_password(email)

        LOGGER.info(get_log_msg(self.request, self.request.user))

        return self._handle_error('Validation failed.', status.HTTP_400_BAD_REQUEST)

    def _reset_password(self, email):
        service = reset_password_service(self.repository)

        try:
            service(email)
        except ObjectNotFoundError as e:
            return self._handle_error(e, status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return self._handle_error(e, status.HTTP_400_BAD_REQUEST)
        except InternalError as e:
            return self._handle_error(e, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


# noinspection PyUnusedLocal
class ValidateResetPasswordViewSet(viewsets.ViewSet):
    """
    ValidateResetPasswordViewSet

    Provides api endpoint that takes a password reset token as GET parameter
    and checks if that token is valid.

     **Parameters and return value**

    :allowed: GET
    :auth required: False
    :many: False
    :returns: 204 in case of success
    :returns: only status code is returned
    :error: 400 if token is malformed or expired
    :error: 404 if associated user could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/validatereset/efc51.json' \
        --header 'Content-Type: application/json'
    """
    repository = ResetRepository()
    permission_classes = (AllowAny,)

    def retrieve(self, request, pk=None, format=None):
        """
        Validates the given reset password token
        """
        LOGGER.info(get_log_msg(self.request, request.user))
        return self._validate_reset_token(pk)

    def _validate_reset_token(self, reset_token):
        service = validate_reset_password_service(self.repository)

        try:
            service(reset_token)
        except ObjectNotFoundError as e:
            return self._handle_error(e, status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return self._handle_error(e, status.HTTP_400_BAD_REQUEST)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


# noinspection PyUnusedLocal
class ConfirmResetPasswordViewSet(viewsets.ViewSet):
    """
    ConfirmResetPasswordViewSet

    Provides api endpoint that validates the given reset password token and
    resets the associated :model:`authentication.User` instance's password.

    **Parameters and return value**

    :allowed: POST
    :auth required: False
    :many: False
    :returns: 204 in case of success
    :returns: only status code is returned
    :error: 400 if posted reset token or password are invalid
    :error: 404 if associated :model:`authentication.User` instance
                could not be found
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for POST request**

    curl --request POST \
        --url 'https://api.basement.technology/auth/confirmreset.json' \
        --header 'Content-Type: application/json' \
        --data

        '{

            "resetToken": "efc5158869dc580466dc291901dd8af39f3cd2b50f4",
            "password": "NewPassword"

        }'
    """
    serializer_class = ConfirmSerializer
    repository = ResetRepository()
    validator_repository = GenericRepository(User)
    permission_classes = (AllowAny,)

    def create(self, request, format=None):
        """
        Validates the token and resets users' password
        """
        data = request.data
        serializer = self.serializer_class(data=data,
                                           context={'request': request})

        if serializer.is_valid(raise_exception=False):
            reset_token = serializer.validated_data['resetToken']
            password = serializer.validated_data['password']

            LOGGER.info(get_log_msg(self.request, request.user))
            return self._validate_reset_token(reset_token, password)

        LOGGER.info(get_log_msg(self.request, self.request.user))

        return self._handle_error("Validation failed.", status.HTTP_400_BAD_REQUEST)

    def _validate_reset_token(self, reset_token, password):
        validators = (is_password_length_sufficient(self.validator_repository, settings.MIN_PASSWORD_LENGTH),
                      does_contain_char_classes(self.validator_repository, settings.CHAR_CLASSES))
        service = confirm_reset_password_service(self.repository, validate_many(*validators))

        try:
            service(reset_token, password)
        except ObjectNotFoundError as e:
            return self._handle_error(e, status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return self._handle_error(e, status.HTTP_400_BAD_REQUEST)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)


# noinspection PyUnusedLocal
class ConfirmEmailViewSet(viewsets.ViewSet):
    """
    ConfirmEmailViewSet

    Provides api endpoint that sends an email validation email to the
    authenticated :model:`authentication.User` instance.

    **Parameters and return value**

    :allowed: GET, POST
    :auth required: True
    :many: False
    :returns: 204 in case of success
    :returns: only status code is returned
    :error: 400 if the user has got an invalid email address of none at 
                all or if the given validation token is invalid or expired
    :error: 401 if the request is unauthorized
    :error: 404 if the :model:`authentication.User` instance associated with 
                the given validation token could not be found 
    :error: 429 if the request was throttled
    :error: 500 if an unexpected error occurs

    **Usage example for GET request**

    curl --request GET \
        --url 'https://api.basement.technology/auth/confirmemail.json' \
        --header 'Authorization: Token db1c73de65b111e89072c471feb11e' \
        --header 'Content-Type: application/json'
    """
    serializer_class = ConfirmSerializer
    repository = MailVerificationRepository()
    validator_repository = GenericRepository(User)

    def list(self, request, format=None):
        """
        Sends an email verification email
        """
        LOGGER.info(get_log_msg(self.request, request.user))
        return self._validate_email(request)

    def _validate_email(self, request):
        user = request.user

        validators = (is_email_valid(self.validator_repository),)
        service = validate_email_service(self.repository, validate_many(*validators))

        try:
            service(user)
        except ValidationError as e:
            return self._handle_error(e, status.HTTP_400_BAD_REQUEST)
        except InternalError as e:
            return self._handle_error(e, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, pk=None, format=None):
        """
        Checks the validation token and flags the email address as validated
        """
        LOGGER.info(get_log_msg(self.request, request.user))
        return self._confirm_email(pk)

    def _confirm_email(self, val_token):
        service = confirm_email_service(self.repository)

        try:
            service(val_token)
        except ObjectNotFoundError as e:
            return self._handle_error(e, status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return self._handle_error(e, status.HTTP_400_BAD_REQUEST)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _handle_error(e, status_code):
        content = {settings.ERROR_KEY: str(e)}
        return Response(content, status=status_code)
