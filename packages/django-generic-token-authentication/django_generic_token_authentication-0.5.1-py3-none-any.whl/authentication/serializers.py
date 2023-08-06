from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, read_only=True)
    password = serializers.CharField(max_length=255, required=True)
    username = serializers.CharField(max_length=50, required=True)
    firstName = serializers.CharField(max_length=50, required=False)
    lastName = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        exclude = ('first_name', 'last_name', 'last_login', 'is_superuser', 'is_staff', 'is_active',
                   'date_joined', 'groups', 'user_permissions')


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, read_only=True)
    username = serializers.CharField(max_length=50, required=False, read_only=False)
    email = serializers.EmailField(required=False, read_only=False)
    firstName = serializers.CharField(max_length=50, required=False, read_only=False)
    lastName = serializers.CharField(max_length=50, required=False, read_only=False)
    validated_email = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = User
        exclude = ('first_name', 'last_name', 'password', 'last_login', 'is_superuser', 'is_staff', 'is_active',
                   'date_joined', 'groups', 'user_permissions')


# noinspection PyAbstractClass
class UpdatePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, required=True)


# noinspection PyAbstractClass
class ResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


# noinspection PyAbstractClass
class ConfirmSerializer(serializers.Serializer):
    resetToken = serializers.CharField(required=True)
    password = serializers.CharField(max_length=255, required=True)


# noinspection PyAbstractClass
class RefreshSerializer(serializers.Serializer):
    refreshToken = serializers.CharField(max_length=500,
                                         required=True)
