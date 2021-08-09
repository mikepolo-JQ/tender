from django.apps import AppConfig


class ChatConfig(AppConfig):
    label = "chat"
    name = f"applications.{ label }"
