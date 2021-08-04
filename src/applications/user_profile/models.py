from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    contacts = models.ManyToManyField("self", related_name="contact_of")
    avatar = models.ImageField(blank=True, null=True, default="avatar.png")
