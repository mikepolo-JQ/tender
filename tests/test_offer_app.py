import django
import pytest

django.setup()

import os
import random
import json

from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from applications.offer import tasks

from applications.offer.models import Offer, Review, Store
from applications.user_profile.models import User


def get_test_content():
    return f"test_content_{os.urandom(16).hex()}"


def update_offer_count(count):
    with open("offer_count.txt", "w") as f:
        f.write(str(count))


def get_offer_count():
    with open("offer_count.txt", "r") as f:
        count = f.readline()
        return int(count)


class OfferAppTests(APITestCase):
    admin_username = "admin"
    password = "test_password"
    first_name = "test_first_name"
    last_name = "test_last_name"
    reviews_test_count = 5

    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()

    # def admin_login(self):
    #
    #     User.objects.create_superuser(
    #         username=self.admin_username, password=self.password
    #     )
    #
    #     response = self.client.post(
    #         "/auth/token/login/",
    #         {"username": self.admin_username, "password": self.password},
    #         format="json",
    #     )
    #     token = response.data.get("auth_token")
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    #     return response

    def _login(self, user: User):

        response = self.client.post(
            "/auth/token/login/",
            {"username": user.username, "password": self.password},
            format="json",
        )
        token = response.data.get("auth_token")
        if not token:
            raise User.DoesNotExist("Unable to log in with provided credentials")
        return token

    def test_data_update_from_API(self):
        response = tasks.update_data_file()
        response_dict = json.loads(response)

        self.assertTrue(response_dict["uploaded_count"])

        # global offers_count
        update_offer_count(response_dict["uploaded_count"])

        self.assertJSONEqual(
            response, {"ok": True, "uploaded_count": get_offer_count()}
        )

    def test_data_upload(self):
        response = tasks.upload_data_from_file_to_the_db()
        response_dict = json.loads(response)

        self.assertEqual(response_dict["ok"], True)
        self.assertEqual(response_dict["count"], get_offer_count())
        self.assertEqual(type(response_dict["added"]), int)

    # OFFER TEST
    def test_offer_detail_and_list(self):

        # Offers list test
        response = self.client.get("/api/offer/")

        # self.assertEqual(get_offer_count(), len(response.data))
        # pytest.set_trace()
        for offer_data in response.data:
            self.offer_list_format_tst(offer_data)

        # Single offer test
        random_offer_id = random.randint(
            response.data[0]["id"], response.data[-1]["id"]
        )
        response = self.client.get(f"/api/offer/{random_offer_id}/")

        offer = response.data

        self.assertEqual(offer["id"], random_offer_id)
        self.offer_detail_format_tst(offer)

    # STORE TEST
    def test_store_detail_and_list(self):

        # Store list test
        response = self.client.get("/api/store/")

        for store in response.data:
            self.store_list_format_tst(store)

        # Store detail test (all fields except offers have already been checked)
        random_store_id = random.randint(
            response.data[0]["id"], response.data[-1]["id"]
        )
        response = self.client.get(f"/api/store/{random_store_id}/")

        for offer in response.data["offers"]:
            self.offer_detail_format_tst(offer)

    # REVIEW TEST
    def review_test_owner_and_detail(self):
        author = User.objects.create_user(username="test", password=self.password)

        response = self.client.get("/api/offer/")  # get offer list

        random_offer_id = random.randint(
            response.data[0]["id"], response.data[-1]["id"]
        )

        # Offer list Review test
        self.owner_list_review_tst(
            owner_type="offer", owner_id=random_offer_id, author=author
        )

        # Review detail test
        self.review_detail_format_tst(like_author=author)

        response = self.client.get("/api/store/")  # get store list

        random_store_id = random.randint(
            response.data[0]["id"], response.data[-1]["id"]
        )

        # Store list Review test
        self.owner_list_review_tst(
            owner_type="store", owner_id=random_store_id, author=author
        )

    # Testing offer data in format OfferListSerializer
    def offer_list_format_tst(self, offer: dict):
        self.assertTrue(offer["id"])
        self.assertEqual(type(offer["id"]), int)

        self.assertTrue(offer["title"])
        self.assertEqual(type(offer["title"]), str)

        self.assertEqual(type(offer["rating"]), float)

        self.assertTrue(offer["store"])
        self.assertEqual(type(offer["store"]), str)

    # Testing store data in format StoreListSerializer
    def store_list_format_tst(self, store):
        self.assertTrue(store["id"])
        self.assertEqual(type(store["id"]), int)

        self.assertTrue(store["name"])
        self.assertEqual(type(store["name"]), str)

        self.assertEqual(type(store["rating"]), float)

        for offer_data in store["offers"]:
            self.offer_list_format_tst(offer_data)

    # Testing offer data in format OfferDetailSerializer
    def offer_detail_format_tst(self, offer):

        self.assertTrue(type(offer["categories"]), list[str])
        self.assertTrue(len(offer["categories"]))

        self.assertTrue(type(offer["types"]), list[str])

        self.assertEqual(type(offer["rating"]), float)

        self.assertTrue(offer["lmd_id"])
        self.assertEqual(type(offer["lmd_id"]), str)

        self.assertEqual(type(offer["offer_text"]), str)

        self.assertEqual(type(offer["offer_value"]), str)

        self.assertEqual(type(offer["description"]), str)

        self.assertEqual(type(offer["featured"]), bool)

        self.assertEqual(type(offer["url"]), str)
        self.assertTrue(offer["url"])

        self.assertTrue(offer["start_date"])
        self.assertTrue(offer["end_date"])

        offer_store = offer["store"]
        self.assertTrue(offer_store["id"])
        self.assertEqual(type(offer_store["id"]), int)

        self.assertTrue(offer_store["name"])
        self.assertEqual(type(offer_store["name"]), str)

    # Testing user data in format UserListSerializer
    def user_list_format_tst(self, user):
        self.assertTrue(user["id"])
        self.assertEqual(type(user["id"]), int)
        self.assertEqual(type(user["username"]), str)
        self.assertTrue(
            user["avatar"].startswith(f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/")
        )

    # Testing reviews data in format ReviewListSerializer
    # Set filter to True to disable certain checks (for ReviewDetailSerializer)
    def review_list_format_tst(self, review, detail_filter=False):
        self.assertTrue(review["id"])
        self.assertEqual(type(review["id"]), int)

        if not detail_filter:
            for children in review["children"]:
                self.review_list_format_tst(children)
            self.assertEqual(type(review["likes_count"]), int)

        self.assertEqual(type(review["rating_value"]), int)

        self.assertEqual(type(review["content"]), str)
        self.assertTrue(review["content"])

        self.assertTrue(review["created_at"])
        self.assertTrue(review["updated_at"])

        self.user_list_format_tst(review["author"])

    # Testing reviews data in format ReviewDetailSerializer
    def review_detail_format_tst(self, like_author):
        review = self.client.get(f"/api/review/1/").data

        self.review_list_format_tst(review, detail_filter=True)

        self.assertEqual(type(review["content_type"]), str)
        self.assertTrue(review["content_type"])

        owner = review["owner"]
        test_worker = {
            "offer": self.offer_list_format_tst,
            "store": self.store_list_format_tst,
        }.get(review["content_type"])
        if not test_worker:
            raise KeyError("Content_type of review isn't valid")
        test_worker(owner)

        # LIKE test
        self.assertFalse(review["likers"])
        token = self._login(like_author)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response_like = self.client.post(f"/api/review/1/like/")
        self.assertEqual(response_like.status_code, 200)

        review_like = self.client.get(f"/api/review/1/").data
        self.assertTrue(review_like["likers"])
        for liker in review_like["likers"]:
            self.user_list_format_tst(liker)

    def owner_list_review_tst(self, owner_type: str, owner_id: int, author: User):
        reviews_count = self.reviews_test_count

        owner_model = {"offer": Offer, "store": Store}.get(owner_type.lower())
        if not owner_model:
            raise KeyError("Owner model isn't found.")
        owner = owner_model.objects.get(pk=owner_id)

        for _ in range(reviews_count):
            r = Review.objects.create(
                author=author, owner=owner, content=get_test_content()
            )
            Review.objects.create(
                author=author, owner=owner, content=get_test_content(), parent=r
            )

        response = self.client.get(f"/api/{owner_type.lower()}/{owner_id}/reviews/")

        for review in response.data:
            self.review_list_format_tst(review)

        # create test
        # check owner rating before update
        owner_resp = self.client.get(f"/api/{owner_type.lower()}/{owner_id}/")
        self.assertFalse(owner_resp.data["rating"])

        test_content = get_test_content()
        test_rating_value = 5
        data = {"content": test_content, "rating_value": test_rating_value}

        token = self._login(author)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post(
            f"/api/{owner_type.lower()}/{owner_id}/reviews/", data=data
        )
        self.assertEqual(response.status_code, 201)
        self.review_list_format_tst(response.data)
        self.assertEqual(response.data["content"], test_content)
        self.assertEqual(response.data["rating_value"], test_rating_value)

        # check owner rating after update
        owner_resp = self.client.get(f"/api/{owner_type.lower()}/{owner_id}/")
        self.assertTrue(owner_resp.data["rating"])
