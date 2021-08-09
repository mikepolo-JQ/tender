from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    ONLINE_STATUS_CHOICES = [
        ("ON", "Online"),
        ("OFF", "Offline"),
    ]

    contacts = models.ManyToManyField("self", related_name="contact_of")
    avatar = models.ImageField(blank=True, null=True, default="avatar.png")
    status_chat = models.CharField(
        max_length=7, choices=ONLINE_STATUS_CHOICES, default="Offline"
    )

    def get_group_name(self):
        return f"user_{self.pk}"
