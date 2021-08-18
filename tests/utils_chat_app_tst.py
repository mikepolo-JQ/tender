import os

from django.conf import settings
from rest_framework.test import APIClient

from applications.chat.models import Chat
from applications.user_profile.models import User

password = "1"


def get_token(user: User):
    client = APIClient()

    response = client.post(
        "/auth/token/login/",
        {"username": user.username, "password": password},
        format="json",
    )
    token = response.data.get("auth_token")
    if not token:
        raise User.DoesNotExist("Unable to log in with provided credentials")
    return token


def author_data_in_format_list_tst(data: dict, user: User):
    author = data["author"]
    assert author["id"] == user.id
    assert author["username"] == user.username
    assert (
        author["avatar"]
        == f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/{user.avatar}"
    )


def user_format_list_tst(data: dict, user: User):
    assert data["id"] == user.id
    assert data["username"] == user.username
    assert (
        data["avatar"] == f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/{user.avatar}"
    )


def get_user() -> User:
    return User.objects.create_user(
        username=f"test_username_{os.urandom(8).hex()}", password=password
    )


def get_chat_for_users(first_user: User, second_user: User) -> Chat:
    chat = Chat.objects.create()
    chat.users.add(first_user, second_user)
    chat.save()
    return chat


def delete_test_objects_from_list(object_list: list) -> None:
    for obj in object_list:
        obj.delete()
