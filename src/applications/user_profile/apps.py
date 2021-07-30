from django.apps import AppConfig


class UserProfileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    label = "user_profile"
    name = f"applications.{ label }"
