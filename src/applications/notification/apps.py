from django.apps import AppConfig


class NotificationConfig(AppConfig):
    label = "notification"
    name = f"applications.{ label }"
