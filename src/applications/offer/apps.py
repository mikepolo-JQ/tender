from django.apps import AppConfig


class OfferConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    label = "offer"
    name = f"applications.{ label }"
