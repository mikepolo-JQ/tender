import asyncio

import django
from django.conf import settings

django.setup()

import os
from asgiref.sync import sync_to_async

from applications.chat.models import Chat, Message
from applications.user_profile.models import User
from rest_framework.test import APITestCase, APIClient

import pytest

from applications.chat.consumers import ChatConsumer
from channels.testing import WebsocketCommunicator
from tests.utils_chat_app_tst import password, get_token, author_data_in_format_list_tst


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_consumer():

    user = await sync_to_async(User.objects.create_user)(
        username=f"test_username_{os.urandom(8).hex()}", password=password
    )
    token = await sync_to_async(get_token)(user)
    talker = await sync_to_async(User.objects.create_user)(
        username=f"test_username_{os.urandom(8).hex()}", password=password
    )

    chat = await sync_to_async(Chat.objects.create)()
    await sync_to_async(chat.users.add)(user, talker)
    await sync_to_async(chat.save)()

    headers = {
        "Authorization": f"Token {token}",
        "chat_pk": chat.pk,
        "user_pk": user.pk,
    }

    # Test a normal connection
    communicator = WebsocketCommunicator(
        ChatConsumer(), path=f"/ws/chat/{chat.pk}", headers=headers
    )

    connected, _ = await communicator.connect()

    assert connected

    # Message creating Test
    message_content = "Hello, Mike!"

    await communicator.send_json_to({"command": "create", "content": message_content})

    response = await communicator.receive_json_from()

    assert response.get("command") == "create"

    message = response["message"]
    assert type(message["id"]) is int
    assert not message["edited"]
    assert message["content"] == message_content

    await sync_to_async(author_data_in_format_list_tst)(data=message, user=user)

    # Message update Test
    new_message_content = f"content_{os.urandom(8).hex()}"
    await communicator.send_json_to(
        {
            "command": "update",
            "content": new_message_content,
            "message_pk": message["id"],
        }
    )

    response = await communicator.receive_json_from()

    assert response["command"] == "update"
    assert type(response["message"]["id"]) is int
    assert response["message"]["content"] == new_message_content
    await sync_to_async(author_data_in_format_list_tst)(response["message"], user)

    # Message deleting Test
    failed_message_id = 0
    await communicator.send_json_to(
        {"command": "delete", "message_pk_list": [message["id"], failed_message_id]}
    )
    response = await communicator.receive_json_from()

    assert response.get("command") == "delete"
    assert response["message_deleted_list"][0] == message["id"]
    assert response["message_failed_list"][0] == failed_message_id

    # Talker typing Test
    await communicator.send_json_to({"command": "typing"})

    response = await communicator.receive_json_from()

    assert response["command"] == "typing"
    await sync_to_async(author_data_in_format_list_tst)(data=response, user=user)

    await communicator.disconnect()


def user_format_list_tst(data: dict, user: User):
    assert data["id"] == user.id
    assert data["username"] == user.username
    assert (
        data["avatar"] == f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/{user.avatar}"
    )


def test_my_chats_url():
    client = APIClient()
    user = User.objects.create_user(
        username=f"test_username_{os.urandom(8).hex()}", password=password
    )
    token = get_token(user)

    talker = User.objects.create_user(
        username=f"test_username_{os.urandom(8).hex()}", password=password
    )

    chat = Chat.objects.create()
    chat.users.add(user, talker)
    chat.save()

    message = Message.objects.create(
        content=f"content_{os.urandom(8).hex()}", author=user, chat=chat
    )
    chat.messages.add(message)

    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    response = client.get("/api/chat/")

    assert response.status_code == 200
    for chat in response.data:
        assert type(chat["id"]) is int
        try:
            user_format_list_tst(data=chat["users"][0], user=user)
            user_format_list_tst(data=chat["users"][1], user=talker)
        except AssertionError:
            user_format_list_tst(data=chat["users"][0], user=talker)
            user_format_list_tst(data=chat["users"][1], user=user)

        assert not chat["name"]

        last_message = chat["last_message"]
        assert last_message["id"] == message.pk
        assert last_message["edited"] == message.edited
        assert last_message["content"] == message.content

        author_data_in_format_list_tst(data=last_message, user=user)


if __name__ == "__main__":
    # asyncio.run(test_consumer())
    test_my_chats_url()
