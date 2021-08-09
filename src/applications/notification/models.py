from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Notification(models.Model):
    name = models.CharField(null=True, blank=True, max_length=50, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        User, related_name="notifications", on_delete=models.CASCADE
    )

    content = models.TextField(null=True, blank=False)
    viewed = models.BooleanField(default=False)
    json_data = models.JSONField(default=None, null=True, blank=True)

    def save(self, send=True, *args, **kwargs):
        super(Notification, self).save(*args, **kwargs)

        if send:
            channel_layer = get_channel_layer()
            notifications_count = Notification.objects.filter(
                viewed=False, user=self.user
            ).count()

            data = {
                "count": notifications_count,
                "content": self.content,
                "data": self.json_data,
                "name": self.name,
            }

            async_to_sync(channel_layer.group_send)(
                self.user.get_group_name(),
                {
                    "type": "notification_send",
                    "data": data,
                },
            )

    class Meta:
        ordering = ["-created_at"]
