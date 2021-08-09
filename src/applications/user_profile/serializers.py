from applications.user_profile.models import User
from rest_framework import serializers


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "id", "avatar"]


class UserDetailSerializer(serializers.ModelSerializer):

    contacts = UserListSerializer(many=True)

    class Meta:
        model = User
        exclude = ("password", "date_joined", "groups", "user_permissions")


class UserContactsSerializer(serializers.ModelSerializer):

    # contacts = UserListSerializer(many=True)
    username = serializers.ReadOnlyField()
    avatar = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ["id", "username", "avatar", "contacts"]
