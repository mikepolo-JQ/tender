from django.urls import path

from applications.notification import views
from applications.notification.apps import NotificationConfig


app_name = NotificationConfig.label

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="notifications"),
]
