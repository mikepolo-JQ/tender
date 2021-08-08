from django.contrib import admin

from applications.notification.models import Notification


@admin.register(Notification)
class NotificationAdminModel(admin.ModelAdmin):
    pass
