from rest_framework import permissions

from applications.chat.models import Chat


class AccessForChat(permissions.BasePermission):
    def has_permission(self, request, view):
        chat_pk = request.parser_context["kwargs"]["pk"]
        chat = Chat.objects.get(pk=chat_pk)
        return self.has_object_permission(request, view, chat)

    def has_object_permission(self, request, view, obj):
        pass
        return request.user in obj.users.all()


def access_for_chat(user, chat_pk):
    """
    permissions AccessForChat for WebSocket
    """
    try:
        chat = Chat.objects.get(pk=chat_pk)
    except Chat.DoesNotExist:
        return False
    return user in chat.users.all()
