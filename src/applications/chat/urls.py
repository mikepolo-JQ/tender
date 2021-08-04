from django.urls import path

from applications.chat import views
from applications.chat.apps import ChatConfig


app_name = ChatConfig.label

urlpatterns = [
    path("test/", views.TestChatView.as_view(), name='test'),
]
