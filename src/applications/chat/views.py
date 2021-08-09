from django.views.generic import TemplateView
from rest_framework import generics, permissions, mixins, status
from rest_framework.response import Response

from applications.chat import serializers
from applications.chat.models import Message, Chat
from applications.chat.service import AccessForChat


class TestChatView(TemplateView):
    template_name = "chat/test.html"


class MessageListView(generics.ListAPIView, generics.DestroyAPIView):
    permission_classes = [AccessForChat, ]

    model = Message
    serializer_class = serializers.MessageSerializer

    def get_queryset(self):
        chat_pk = self.kwargs.get("pk")
        try:
            queryset = Chat.objects.get(pk=chat_pk).messages.all()
            return queryset
        except Chat.DoesNotExist:
            return {"error": "chat does not exist"}

    def destroy(self, request, *args, **kwargs):
        instance = Chat.objects.get(pk=kwargs.get("pk"))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChatListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    model = Chat
    serializer_class = serializers.ChatDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return user.chats.all()


class CreateChatView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]

    model = Chat
    serializer_class = serializers.ChatCreateSerializer
