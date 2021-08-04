# chat/consumers.py
import json
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer

from applications.chat.models import Chat, Message
from applications.user_profile.models import User


def writes_message(s, data):
    talker_pk = data["talker_pk"]
    chat_pk = data["chat_pk"]

    # Send message to talker
    async_to_sync(s.channel_layer.group_send)(
        f"chat_{chat_pk}",
        {
            "type": "is_typing",
            "command": data["command"],
            "author": data["author"],
            "chat_pk": data["chat_pk"],
        },
    )


def copy_message(s, data):
    message_pk = data["message_pk"]
    author_pk = data["author_pk"]

    message = Message.objects.filter(pk=message_pk).first()

    async_to_sync(s.channel_layer.group_send)(
        f"profile_{author_pk}",
        {
            "type": "copy_for_author",
            "content": message.content,
            "message_pk": message.pk,
            "author_pk": author_pk,
            "datetime": message.get_datetime,
            "chat_pk": data["chat_pk"],
        },
    )


# CREATE and send message to room group
def create_message(s, data):
    content = data["content"]

    # Send message to room group
    async_to_sync(s.channel_layer.group_send)(
        s.room_group_name,
        {
            "type": "chat_message",
            "command": "create",
            "content": content,
        },
    )


# DELETE and send message to room group
def delete_messages(s, data):
    message_pk_list = data["pk_list"]
    chat_pk = data["chat_pk"]

    message_deleted_list = list()
    message_failed_list = list()

    for pk in message_pk_list:
        try:
            Message.objects.get(pk=pk).delete()
            message_deleted_list.append(pk)
        except:
            message_failed_list.append(pk)

    # Send message to room group
    async_to_sync(s.channel_layer.group_send)(
        s.group_name,
        {
            "type": "delete_message",
            "message_deleted_list": message_deleted_list,
            "message_failed_list": message_failed_list,
            "chat_pk": chat_pk,
            "author_pk": data["author_pk"],
        },
    )


command_handlers = {
    "create": create_message,
    "delete": delete_messages,
    "typing": writes_message,
}


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"room_{self.room_name}"

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
        text_data_json = json.loads(text_data)

        command = text_data_json["command"]
        command_handlers[command](self, text_data_json)

    # Receive message from room group
    def chat_message(self, event):
        content = event["content"]

        # Send message to WebSocket
        self.send(
            text_data=json.dumps(
                {
                    "command": "create",
                    "content": content,
                    # "message_pk": pk,
                    # "author_pk": author_pk,
                    # "datetime": datetime,
                    # "chat_pk": chat_pk,
                }
            )
        )

    # def delete_message(self, event):
    #
    #     # Send message to WebSocket
    #     self.send(
    #         text_data=json.dumps(
    #             {
    #                 "command": "delete",
    #                 "message_deleted_list": event["message_deleted_list"],
    #                 "message_failed_list": event["message_failed_list"],
    #                 "chat_pk": event["chat_pk"],
    #                 "author_pk": event["author_pk"],
    #             }
    #         )
    #     )
    #
    # def is_typing(self, event):
    #
    #     # Send message to WebSocket
    #     self.send(
    #         text_data=json.dumps(
    #             {
    #                 "command": event["command"],
    #                 "author": event["author"],
    #                 "chat_pk": event["chat_pk"],
    #             }
    #         )
    #     )
