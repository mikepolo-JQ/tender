from applications.user_profile.models import User
from rest_framework import serializers


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "id", 'avatar']


class UserDetailSerializer(serializers.ModelSerializer):

    contacts = UserListSerializer(many=True)

    class Meta:
        model = User
        exclude = ("password", "date_joined", "groups", "user_permissions")
