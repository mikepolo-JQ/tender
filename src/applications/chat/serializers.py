from rest_framework import serializers
from applications.chat.models import Message, Chat
from applications.user_profile.serializers import UserListSerializer


class ChatDetailSerializer(serializers.ModelSerializer):

    users = UserListSerializer(many=True)
    last_message = serializers.SerializerMethodField()

    def get_last_message(self, chat):
        last = chat.messages.all().last()
        return MessageSerializer(last).data

    class Meta:
        model = Chat
        exclude = ["updated_at"]


class MessageSerializer(serializers.ModelSerializer):

    author = UserListSerializer(read_only=True)
    datetime = serializers.SerializerMethodField()

    def get_datetime(self, msg):
        return msg.get_datetime

    class Meta:
        model = Message
        exclude = ["chat", "created_at", "updated_at"]


class ChatCreateSerializer(serializers.ModelSerializer):

    name = serializers.ReadOnlyField()

    class Meta:
        model = Chat
        fields = "__all__"
