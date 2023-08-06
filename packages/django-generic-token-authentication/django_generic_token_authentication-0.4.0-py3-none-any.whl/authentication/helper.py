import random
import string

from django.conf import settings
from utility.functions import get_uuid1


def get_token_id():
    uuid = str(get_uuid1())
    return uuid.replace("-", "")


def get_token():
    return get_rand_str(settings.TOKEN_LENGTH - 32)


def get_refresh_token():
    return get_rand_str(settings.REFRESH_TOKEN_LENGTH)


def get_rand_str(l):
    t = ''.join(random.SystemRandom().choice(string.hexdigits
                                             + string.digits) for _ in range(l))
    return t.lower()
