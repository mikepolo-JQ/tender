from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import generics

from api.serializers import UserSerializer

User = get_user_model()


# Create your views here.
class UserListView(generics.ListAPIView):
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer
