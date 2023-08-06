from datetime import timedelta

SECRET_KEY = '2^mza*qpug3+htv7jxecatc0w&rluw!b#2cf9r*+&3fj8a2i66'
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'utility',
    'authentication',
    'tests',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django-generic-rest.db',
    }
}
AUTH_USER_MODEL = 'tests.User'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

TOKEN_LENGTH = 64
TOKEN_EXPIRY = timedelta(hours=1)
REFRESH_TOKEN_LENGTH = 128
REFRESH_TOKEN_EXPIRY = timedelta(days=1)
ROOT_URLCONF = 'authentication.urls'
MIN_PASSWORD_LENGTH = 4
CHAR_CLASSES = 1
ERROR_KEY = 'Error'

HOST = 'localhost:8000'
DEFAULT_FROM_EMAIL = 'Token Auth <noreply@djangotokenauth.test>'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

RESET_TOKEN_EXPIRY = timedelta(days=1)
VAL_TOKEN_EXPIRY = timedelta(days=3)
