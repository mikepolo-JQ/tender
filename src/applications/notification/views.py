from rest_framework import generics, permissions

from applications.notification import serializers
from applications.notification.models import Notification


class NotificationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    model = Notification
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        user = self.request.user

        return user.notifications.all()
