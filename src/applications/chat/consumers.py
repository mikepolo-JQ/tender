import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer


from applications.chat.models import Chat, Message
from applications.chat.serializers import MessageSerializer
from applications.chat.service import access_for_chat

from applications.user_profile.serializers import UserListSerializer


def typing_message(s, data):

    # Send message to talker
    async_to_sync(s.channel_layer.group_send)(
        s.room_group_name,
        {
            "type": "is_typing",
            "command": data["command"],
            "author": UserListSerializer(s.user).data,
        },
    )


# CREATE and send message to room group
def create_message(s, data):

    try:
        msg_content = data["content"]
    except KeyError:
        async_to_sync(s.channel_layer.group_send)(
            s.user_room_name,
            {"type": "error_response", "detail": "Content isn't found."},
        )
        return

    msg = Message.objects.create(
        content=msg_content, author=s.user, chat_id=s.chat_name
    )

    # Send message to room group
    async_to_sync(s.channel_layer.group_send)(
        s.room_group_name,
        {
            "type": "chat_message",
            "command": "create",
            "message": MessageSerializer(msg).data,
        },
    )


# DELETE and send message to room group
def delete_messages(s, data):
    message_pk_list = data["message_pk_list"]
    user = s.user

    message_deleted_list = list()
    message_failed_list = list()

    for pk in message_pk_list:
        try:
            Message.objects.get(pk=pk, author=user).delete()
            message_deleted_list.append(pk)
        except Message.DoesNotExist:
            message_failed_list.append(pk)

    # Send message to room group
    async_to_sync(s.channel_layer.group_send)(
        s.room_group_name,
        {
            "type": "delete_message",
            "message_deleted_list": message_deleted_list,
            "message_failed_list": message_failed_list,
        },
    )


def update_message(s, data):

    try:
        msg_content = data["content"]
        message_pk = data["message_pk"]
    except KeyError:
        async_to_sync(s.channel_layer.group_send)(
            s.user_room_name,
            {"type": "error_response", "detail": "Bad request."},
        )
        return

    try:
        msg = Message.objects.get(pk=message_pk)
        msg.content = msg_content
        msg.save()
    except Message.DoesNotExist:
        async_to_sync(s.channel_layer.group_send)(
            s.user_room_name,
            {"type": "error_response", "detail": "Message isn't found."},
        )
        return

    # Send message to room group
    async_to_sync(s.channel_layer.group_send)(
        s.room_group_name,
        {
            "type": "message_update",
            "message": MessageSerializer(msg).data,
        },
    )


command_handlers = {
    "create": create_message,
    "update": update_message,
    "delete": delete_messages,
    "typing": typing_message,
}


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.chat_name = self.scope["url_route"]["kwargs"]["chat_name"]
        self.room_group_name = f"room_{self.chat_name}"
        self.permissions = False
        self.user = self.scope["user"]
        self.user_room_name = f"user_{self.user.pk}"

        if access_for_chat(user=self.user, chat_pk=self.chat_name):

            self.permissions = True

            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )

        async_to_sync(self.channel_layer.group_add)(
            self.user_room_name, self.channel_name
        )

        self.accept()

        # permissions check
        if not self.permissions:
            async_to_sync(self.channel_layer.group_send)(
                self.user_room_name,
                {
                    "type": "error_response",
                    "detail": "You do not have permission to perform this action.",
                    "disconnect": True,
                },
            )

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
        async_to_sync(self.channel_layer.group_discard)(
            self.user_room_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):

        text_data_json = json.loads(text_data)

        try:
            command = text_data_json["command"]
            command_handlers[command](self, text_data_json)
        except KeyError:
            async_to_sync(self.channel_layer.group_send)(
                self.user_room_name,
                {"type": "error_response", "detail": "Command isn't found."},
            )
            return

    # Receive message from room group
    def chat_message(self, event):

        # Send message to WebSocket
        self.send(
            text_data=json.dumps({"command": "create", "message": event["message"]})
        )

    def message_update(self, event):
        self.send(
            text_data=json.dumps({
                "command": "update_message",
                "message": event["message"]
            })
        )

    def error_response(self, event):
        self.send(text_data=json.dumps({"detail": event["detail"]}))
        try:
            if event["disconnect"]:
                self.close(1000)
        except KeyError:
            pass

    def delete_message(self, event):

        # Send message to WebSocket
        self.send(
            text_data=json.dumps(
                {
                    "command": "delete",
                    "message_deleted_list": event["message_deleted_list"],
                    "message_failed_list": event["message_failed_list"],
                }
            )
        )

    def is_typing(self, event):

        # Send message to WebSocket
        self.send(
            text_data=json.dumps(
                {
                    "command": event["command"],
                    "author": event["author"],
                }
            )
        )
