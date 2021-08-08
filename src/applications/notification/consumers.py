import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer


from applications.chat.models import Chat, Message
from applications.chat.serializers import MessageSerializer
from applications.chat.service import access_for_chat
from applications.notification.models import Notification
from applications.notification import serializers

from applications.user_profile.serializers import UserListSerializer


def get_notification_list(s, _data):
    try:
        notifications = Notification.objects.filter(user=s.user, viewed=False)
    except Notification.DoesNotExest:
        async_to_sync(s.channel_layer.group_send)(
            s.group_roon_name,
            {"type": "error_response", "detail": "Notification isn't found."},
        )
        return

    data = list()

    for notification in notifications:
        data.append(serializers.NotificationSerializer(notification).data)

    async_to_sync(s.channel_layer.group_send)(
        s.room_group_name,
        {
            "type": "notification_list",
            "notification_list": data,
        },
    )


# CREATE and send message to room group
def notification_view(s, data):

    try:
        notification_pk_list = data["notification_pk_list"]
    except KeyError:
        async_to_sync(s.channel_layer.group_send)(
            s.room_group_name,
            {"type": "error_response", "detail": "Notification list isn't found."},
        )
        return

    viewed_list = list()
    failed_list = list()

    for pk in notification_pk_list:
        try:
            notification = Notification.objects.get(pk=pk)
            notification.viewed = True
            notification.save(send=False)
            viewed_list.append(pk)
        except Notification.DoesNotExist:
            failed_list.append(pk)

    # Send message to room group
    async_to_sync(s.channel_layer.group_send)(
        s.room_group_name,
        {
            "type": "notification_viewed",
            "viewed_list": viewed_list,
            "failed_list": failed_list,
        },
    )


command_handlers = {
    "get_list": get_notification_list,
    "view": notification_view,
}


class NotificationConsumer(WebsocketConsumer):
    def connect(self):

        self.user = self.scope["user"]

        # permissions check
        if self.user.is_anonymous:
            self.close(1000)

        self.room_group_name = self.user.get_group_name()

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

        try:
            command = text_data_json["command"]
            command_handlers[command](self, text_data_json)
        except KeyError:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {"type": "error_response", "detail": "Command isn't found."},
            )
            return

    def notification_list(self, event):
        self.send(
            text_data=json.dumps(
                {"command": "get_list", "notification_list": event["notification_list"]}
            )
        )

    # Receive message from room group
    def notification_send(self, event):

        # Send message to WebSocket
        self.send(
            text_data=json.dumps(
                {
                    "command": "notification",
                    "count": event["data"]["count"],
                    "content": event["data"]["content"],
                }
            )
        )

    def notification_viewed(self, event):
        self.send(
            text_data=json.dumps(
                {
                    "command": "notification_view",
                    "viewed_list": event["viewed_list"],
                    "failed_list": event["failed_list"],
                }
            )
        )

    def error_response(self, event):
        self.send(text_data=json.dumps({"detail": event["detail"]}))
        try:
            if event["disconnect"]:
                self.close(1000)
        except KeyError:
            pass
