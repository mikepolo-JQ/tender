from django.urls import path

from applications.chat import views
from applications.chat.apps import ChatConfig


app_name = ChatConfig.label

urlpatterns = [
    path("test/", views.TestChatView.as_view(), name="test"),
    path("", views.ChatListView.as_view(), name="my_chats"),
    path("<int:pk>/", views.MessageListView.as_view(), name="messages"),
]
