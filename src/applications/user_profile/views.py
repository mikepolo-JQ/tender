from applications.user_profile.models import User
from rest_framework import generics, permissions

from applications.user_profile import serializers


class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]

    model = User
    queryset = User.objects.filter()
    serializer_class = serializers.UserDetailSerializer
