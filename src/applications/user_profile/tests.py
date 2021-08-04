import os

from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from applications.user_profile.models import User


def get_username():
    nonce = os.urandom(8).hex()
    return f"test_name_{nonce}"


class UserProfileTests(APITestCase):
    password = "test_password"
    first_name = "test_first_name"
    last_name = "test_last_name"

    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()
        self.username = get_username()

    def signUp(self, username):
        response = self.client.post(
            "/auth/users/",
            {"username": username, "password": self.password},
            format="json",
        )
        return response

    def login(self, username):
        self.signUp(self.username)

        response = self.client.post(
            "/auth/token/login/",
            {"username": username, "password": self.password},
            format="json",
        )
        return response

    def test_create_account(self):
        response = self.signUp(self.username)

        assert response.status_code == 201
        assert response.data["username"] == self.username
        assert response.data["id"] == 1
        assert not response.data["email"]

    def test_login(self):
        response = self.login(self.username)
        assert response.status_code == 200
        assert response.data.get("auth_token")

    def test_profile_page(self):
        self.signUp(self.username)

        user = User.objects.get()
        token = self.login(username=user.username).data["auth_token"]

        response = self.client.get(path=f"/api/profile/{user.id}/")

        assert response.status_code == 200
        assert response.data["username"] == self.username
        assert (
            response.data["avatar"]
            == f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/avatar.png"
        )
        assert not len(response.data["contacts"])

        # EDIT USER PROFILE
        # create contact for user
        contact_username = get_username()
        contact_id = self.signUp(contact_username).data["id"]
        user.contacts.add(User.objects.get(pk=contact_id))

        # edit data
        patch_data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

        # user AUTHORIZATION
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.patch(
            path=f"/api/profile/{user.id}/", data=patch_data, format="json"
        )

        assert response.data["first_name"] == self.first_name
        assert response.data["last_name"] == self.last_name
        assert len(response.data["contacts"])

        assert response.data["contacts"][0]["id"] == contact_id
        assert response.data["contacts"][0]["username"] == contact_username
