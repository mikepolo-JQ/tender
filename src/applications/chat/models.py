from datetime import datetime, timedelta
from django.db import models

from applications.user_profile.models import User


class Chat(models.Model):
    name = models.CharField(null=False, max_length=50, default="chat")
    updated_at = models.DateTimeField(auto_now=True)

    users = models.ManyToManyField(
        User,
        related_name="chats",
    )

    @property
    def last_message(self):
        self.message_set.update()
        last = self.message_set.all().last()
        return last

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["-updated_at"]


class Message(models.Model):
    created_at = models.DateTimeField(default=datetime.now)

    content = models.TextField(null=False, default="content")

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def format_date(self) -> str:
        return self.created_at.strftime("%d.%m.%Y")

    @property
    def format_time(self) -> str:
        return self.created_at.strftime("%H:%M")

    @property
    def get_datetime(self):
        today = datetime.now().date()
        msg_date = self.created_at.date()
        yesterday = today - timedelta(1)

        if msg_date < yesterday:
            dt = f"{self.format_date} {self.format_time}"
        elif today > msg_date:
            dt = f"Вчера {self.format_time}"
        else:
            dt = f"{self.format_time}"

        return dt

    def __str__(self):
        return f"user:{self.author} in {self.created_at}"

    class Meta:
        ordering = ["created_at"]
