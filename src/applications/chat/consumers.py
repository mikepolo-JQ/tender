import json

from asgiref.sync import async_to_sync
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
            "author": UserListSerializer(s.scope["user"]).data,
        },
    )


# CREATE and send message to room group
def create_message(s, data):

    msg = Message.objects.create(
        content=data["content"], author=s.scope["user"], chat_id=s.chat_name
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
    user = s.scope["user"]

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


command_handlers = {
    "create": create_message,
    "delete": delete_messages,
    "typing": typing_message,
}


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.chat_name = self.scope["url_route"]["kwargs"]["chat_name"]
        self.room_group_name = f"room_{self.chat_name}"
        self.permissions = True

        if not access_for_chat(user=self.scope["user"], chat_pk=self.chat_name):
            self.permissions = False
            self.room_group_name = f"user_pk_{self.scope['user'].pk}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):

        # permissions check
        if not self.permissions:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {"type": "no_access"},
            )
            return

        text_data_json = json.loads(text_data)

        command = text_data_json["command"]
        command_handlers[command](self, text_data_json)

    # Receive message from room group
    def chat_message(self, event):

        # Send message to WebSocket
        self.send(
            text_data=json.dumps({"command": "create", "message": event["message"]})
        )

    def no_access(self, _event):
        self.send(
            text_data=json.dumps(
                {"detail": "You do not have permission to perform this action."}
            )
        )

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
