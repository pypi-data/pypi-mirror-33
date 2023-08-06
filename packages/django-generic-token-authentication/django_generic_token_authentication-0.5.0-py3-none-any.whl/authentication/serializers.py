from django.conf import settings
from rest_framework import serializers

from authentication.models import User


class RegisterSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, read_only=True)
    password = serializers.CharField(max_length=255, required=True)
    username = serializers.CharField(max_length=50, required=True)
    firstName = serializers.CharField(max_length=50, required=False)
    lastName = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ('id',
                  'password',
                  'username',
                  'email',
                  'firstName',
                  'lastName')


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, read_only=True)
    username = serializers.CharField(max_length=50, required=False, read_only=False)
    email = serializers.EmailField(required=False, read_only=False)
    firstName = serializers.CharField(max_length=50, required=False, read_only=False)
    lastName = serializers.CharField(max_length=50, required=False, read_only=False)
    validated_email = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'email',
                  'firstName',
                  'lastName',
                  'validated_email')


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
