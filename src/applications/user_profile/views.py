import os

from django.conf import settings
from rest_framework.renderers import JSONRenderer

from applications.user_profile.models import User
from rest_framework import generics, permissions

from applications.user_profile import serializers
from applications.user_profile.service import (
    IsYouOrIsAdminOrReadOnly,
    delete_file_from_s3,
)


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsYouOrIsAdminOrReadOnly, ]

    model = User
    queryset = User.objects.filter()
    serializer_class = serializers.UserDetailSerializer

    def perform_update(self, serializer):
        new_avatar = serializer.validated_data.get("avatar", None)
        if new_avatar:
            user = self.get_object()
            old_avatar = user.avatar
            resp = delete_file_from_s3(old_avatar.name)
            assert resp
        super().perform_update(serializer)