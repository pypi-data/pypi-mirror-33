from django.contrib.auth.models import AbstractUser
from django.db import models
from utility.functions import (get_uuid1, get_current_datetime)
from utility.mixins import DictMixin

from authentication.helper import (get_token_id, get_token, get_refresh_token)


class User(AbstractUser, DictMixin):
    """
    Overrides the default Django User, uuid is changed from an auto incremental
    integer field to a uuidv1 field
    """
    id = models.UUIDField(default=get_uuid1, primary_key=True)
    username = models.CharField(max_length=50,
                                unique=True,
                                blank=False,
                                null=False)
    password = models.CharField(max_length=255, blank=False, null=False)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=1, blank=True, null=True)
    last_name = models.CharField(max_length=1, blank=True, null=True)
    firstName = models.CharField(max_length=50, blank=True, null=True)
    lastName = models.CharField(max_length=50, blank=True, null=True)
    validated_email = models.BooleanField(default=False,
                                          blank=False,
                                          null=False)

    def __unicode__(self):
        return "{0}".format(self.id)

    def __str__(self):
        return "{0}".format(self.id)


class AuthToken(models.Model):
    """
    Overrides the default Django Token
    """
    id = models.CharField(max_length=32, default=get_token_id, primary_key=True)
    key = models.CharField(max_length=255, default=get_token, primary_key=False)
    refresh_key = models.CharField(max_length=255, default=get_refresh_token)
    user = models.ForeignKey(User,
                             null=False,
                             blank=False,
                             related_name='auth_token_set',
                             on_delete=models.CASCADE)
    created = models.DateTimeField(null=False,
                                   blank=False,
                                   default=get_current_datetime)

    def __str__(self):
        return "{0}".format(self.id)
