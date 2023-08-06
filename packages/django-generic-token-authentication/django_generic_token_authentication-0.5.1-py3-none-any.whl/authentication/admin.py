from django.contrib import admin
from django.contrib.auth import get_user_model

from authentication.models import AuthToken

User = get_user_model()

admin.site.register(User)
admin.site.register(AuthToken)
