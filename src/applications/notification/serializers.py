from rest_framework import serializers
from applications.chat.models import Message, Chat
from applications.notification.models import Notification
from applications.user_profile.serializers import UserListSerializer


class NotificationSerializer(serializers.ModelSerializer):

    user = UserListSerializer()

    class Meta:
        model = Notification
        fields = "__all__"
