import json
import os
import random
from typing import Optional

from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from applications.offer.models import Offer, Review, Store
from applications.user_profile.models import User
from applications.offer import tasks


offers_count = 421


def get_test_content():
    return f"test_content_{os.urandom(16).hex()}"


class OfferAppTests(APITestCase):
    admin_username = "admin"
    password = "test_password"
    first_name = "test_first_name"
    last_name = "test_last_name"
    reviews_test_count = 5

    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()

    def admin_login(self):

        User.objects.create_superuser(
            username=self.admin_username, password=self.password
        )

        response = self.client.post(
            "/auth/token/login/",
            {"username": self.admin_username, "password": self.password},
            format="json",
        )
        token = response.data.get("auth_token")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        return response

    def test_data_update_from_API(self):
        response = tasks.update_data_file()
        response_dict = json.loads(response)

        self.assertTrue(response_dict["uploaded_count"])

        global offers_count
        offers_count = response_dict["uploaded_count"]

        self.assertJSONEqual(response, {"ok": True, "uploaded_count": offers_count})

    def _data_upload(self):
        response = tasks.upload_data_from_file_to_the_db()
        self.assertJSONEqual(
            response,
            {"ok": True, "count": offers_count, "added": offers_count},
            "Try change data_update_test to True",
        )

    # Testing format offer with OfferListSerializer
    def list_format_offer_tst(self, offer: dict):
        self.assertTrue(offer["id"])
        self.assertEqual(type(offer["id"]), int)

        self.assertTrue(offer["title"])
        self.assertEqual(type(offer["title"]), str)

        self.assertEqual(type(offer["rating"]), float)

        self.assertTrue(offer["store"])
        self.assertEqual(type(offer["store"]), str)

    # Testing format store with StoreListSerializer
    def list_format_store_tst(self, store):
        self.assertTrue(store["id"])
        self.assertEqual(type(store["id"]), int)

        self.assertTrue(store["name"])
        self.assertEqual(type(store["name"]), str)

        self.assertEqual(type(store["rating"]), float)

        for offer_data in store["offers"]:
            self.list_format_offer_tst(offer_data)

    #     Testing format offer with OfferDetailSerializer
    def detail_format_offer_tst(self, offer):

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

    # TEST OFFER STORE
    def test_offerStore(self):
        self._data_upload()

        # Offers list test
        response = self.client.get("/api/offer/")

        self.assertEqual(offers_count, len(response.data))

        for offer_data in response.data:
            self.list_format_offer_tst(offer_data)

        # Single offer test
        random_offer_id = random.randint(
            response.data[0]["id"], response.data[-1]["id"]
        )
        response = self.client.get(f"/api/offer/{random_offer_id}/")

        offer = response.data

        self.assertEqual(offer["id"], random_offer_id)
        self.detail_format_offer_tst(offer)

        # Store list test
        response = self.client.get("/api/store/")

        for store in response.data:
            self.list_format_store_tst(store)

        # Store detail test (all fields except offers have already been checked)
        random_store_id = random.randint(
            response.data[0]["id"], response.data[-1]["id"]
        )
        response = self.client.get(f"/api/store/{random_store_id}/")

        for offer in response.data["offers"]:
            self.detail_format_offer_tst(offer)

    # List of offers reviews test
    # def test_review(self):
    #     self._data_upload()
    #
    #     store = Store.objects.create(name="test_store")
    #     offer = Offer.objects.create(
    #         lmd_id="4214",
    #         offer_value="",
    #         title="",
    #         featured=False,
    #         status="",
    #         start_date="2020-01-01",
    #         end_date="2020-01-02",
    #         store=store,
    #     )
    #     admin = User.objects.create_user(username="test", password="")
    #     # reviews_count = self.reviews_test_count
    #     # for _ in range(reviews_count):
    #     review = Review.objects.create(author=admin, content=get_test_content())
    #     offer.reviews.add(review)
    #
    #     response = self.client.get(f"/api/offer/{offer.pk}/reviews/")
    #     print(response.data, "----------------------------------")
    #
    #     print(response.data, "AFTER")
