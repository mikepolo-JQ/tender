import os

from django.conf import settings
from rest_framework.renderers import JSONRenderer

from applications.user_profile.models import User
from rest_framework import generics, permissions

from applications.user_profile import serializers
from applications.user_profile.service import IsYouOrIsAdminOrReadOnly


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.AllowAny, IsYouOrIsAdminOrReadOnly]

    model = User
    queryset = User.objects.filter()
    serializer_class = serializers.UserDetailSerializer

    # def perform_update(self, serializer):
    #     new_avatar = serializer.validated_data.get('avatar', None)
    #     if new_avatar:
    #         user = self.get_object()
    #         old_avatar = user.avatar
    #         os.remove(settings.MEDIA_ROOT + "/" + old_avatar.name)
    #     super().perform_update(serializer)
