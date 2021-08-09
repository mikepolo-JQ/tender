import json
import os

from django.conf import settings
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.user_profile.models import User
from rest_framework import generics, permissions

from applications.user_profile import serializers
from applications.user_profile.services import (
    IsYouOrIsAdminOrReadOnly,
    delete_file_from_s3, user_contacts_add_delete,
)


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [
        IsYouOrIsAdminOrReadOnly,
    ]

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


class UserAddDeleteToContact(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def patch(self, request, *args, **kwargs):
        return user_contacts_add_delete(self, request, command="add")

    def delete(self, request, *args, **kwargs):
        return user_contacts_add_delete(self, request, command="delete")
