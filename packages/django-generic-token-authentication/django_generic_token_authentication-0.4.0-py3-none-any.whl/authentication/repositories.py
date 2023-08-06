from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from utility.exceptions import (ObjectNotFoundError,
                                ValidationError,
                                InternalError)
from utility.functions import get_current_datetime

from authentication.helper import get_rand_str
from authentication.models import AuthToken, User


class TokenRepository:
    """
    Provides a database abstraction layer for the Token model
    """

    @staticmethod
    def delete_by_user(user):
        AuthToken.objects.filter(user=user).delete()

    @staticmethod
    def create_token(user):
        num_tokens = AuthToken.objects.filter(user=user).count()
        if num_tokens > 9:
            diff = num_tokens - 9
            tokens = AuthToken.objects.filter(user=user)
            ks_to_del = tokens.order_by('created')[:diff].values_list("id",
                                                                      flat=True)
            AuthToken.objects.filter(pk__in=list(ks_to_del)).delete()

        token = AuthToken(user=user)
        uuid = token.id
        key = token.key
        r_key = token.refresh_key
        token.key = make_password(key)
        token.refresh_key = make_password(r_key)
        token.save()
        key = uuid + key
        return key, r_key

    @staticmethod
    def delete_expired_tokens(delta):
        AuthToken.objects.filter(created__lte=get_current_datetime() - delta).delete()

    @staticmethod
    def logout(token):
        try:
            token_id = token[:32]
            user_token = AuthToken.objects.get(id=token_id)
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.',
                                      modelclass='AuthToken')

        if check_password(token[32:], user_token.key):
            user_token.delete()
            return
        else:
            raise ObjectNotFoundError('Object not found.',
                                      modelclass='AuthToken')

    def refresh_token(self, user, token, refresh_token):
        try:
            token_id = token[:32]
            user_token = AuthToken.objects.get(id=token_id)
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.',
                                      modelclass='AuthToken')

        if (check_password(token[32:], user_token.key)
                and check_password(refresh_token, user_token.refresh_key)):
            user_token.delete()
            return self.create_token(user)
        else:
            raise ObjectNotFoundError('Object not found.',
                                      modelclass='AuthToken')


class ResetRepository:
    """
    Provides an abstraction layer for the password reset functionality
    """
    namespace = 'passwd_reset_req'

    def reset_password(self, email):
        # Generate reset token
        if email is None:
            raise ValidationError('Email address has not been set.',
                                  field='email')

        try:
            user = User.objects.filter(email=email).get()
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.', modelclass='User')

        if not user.validated_email:
            raise ValidationError('Email address has not been verified.',
                                  field='email')

        reset_token = signing.dumps({'userId': str(user.id),
                                     'rand': get_rand_str(16)},
                                    salt=self.namespace,
                                    compress=True)

        # Send reset token to user
        subject = 'Password reset'
        body = """Click this link to confirm password
                  reset: {0}/validatereset/{1}.json""".format(settings.HOST,
                                                              reset_token)
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = email
        email_message = EmailMultiAlternatives(subject,
                                               body,
                                               from_email,
                                               [to_email])
        try:
            return email_message.send(), reset_token
        except ConnectionRefusedError:
            raise InternalError('Send email failed.', fct='send')

    def validate_token_and_get_user(self, reset_token):
        # Unsign reset token
        try:
            unsigned_token = signing.loads(reset_token,
                                           max_age=settings.RESET_TOKEN_EXPIRY,
                                           salt=self.namespace)
        except signing.SignatureExpired:
            raise ValidationError('Expired reset request.', field='reset_token')
        except signing.BadSignature:
            raise ValidationError('Invalid reset request.', field='reset_token')

        # Retrieve user
        try:
            user = User.objects.get(id=unsigned_token['userId'])
        except KeyError:
            raise ValidationError('Invalid request.', field='userId')
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.', modelclass='User')

        return user


class MailVerificationRepository:
    """
    Provides an abstraction layer for the verify email functionality
    """
    namespace = 'verify_email_add'

    def send_email_validation(self, user):
        if user.validated_email:
            raise ValidationError('Email has already been verified.',
                                  field='email')

        if user.email is None:
            raise ValidationError('Email address has not been set.',
                                  field='email')

        # Generate validation token
        val_token = signing.dumps({'userId': str(user.id),
                                   'rand': get_rand_str(16)},
                                  salt=self.namespace)

        # Send validation mail
        subject = 'Confirm email address'
        body = """Click this link to confirm your email address:
                  {0}/confirmemail/{1}.json""".format(settings.HOST, val_token)
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email
        email_message = EmailMultiAlternatives(subject,
                                               body,
                                               from_email,
                                               [to_email])
        try:
            return email_message.send(), val_token
        except ConnectionRefusedError:
            raise InternalError('Send email failed.', fct='send')

    def validate_token_and_get_user(self, val_token):
        # Unsign reset token
        try:
            unsigned_token = signing.loads(val_token,
                                           max_age=settings.VAL_TOKEN_EXPIRY,
                                           salt=self.namespace)
        except signing.SignatureExpired:
            raise ValidationError('Expired validation request.',
                                  field='validation_token')
        except signing.BadSignature:
            raise ValidationError('Invalid validation request.',
                                  field='validation_token')

        # Retrieve user
        try:
            user = User.objects.get(id=unsigned_token['userId'])
        except KeyError:
            raise ValidationError('Invalid request.', field='userId')
        except ObjectDoesNotExist:
            raise ObjectNotFoundError('Object not found.', modelclass='User')

        return user
