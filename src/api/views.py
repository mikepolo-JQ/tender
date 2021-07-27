import json

from django.contrib.auth import get_user_model
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
import requests
from dynaconf import settings as _ds

from rest_framework.response import Response

from api.models import Offer, Category
from api.serializers import OfferSerializer
from api.utils import OfferFilter

User = get_user_model()


# Create your views here.
class OfferListView(generics.ListAPIView):
    model = Offer
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = OfferFilter


class DataUpdateView(generics.views.APIView):
    def get(self, request):

        url = "https://linkmydeals.p.rapidapi.com/getOffers/"

        querystring = {
            "API_KEY": _ds.API_KEY,
            "format": "json",
            "incremental": "{incremental}",
            "last_extract": "{last_extract}",
            "off_record": "{off_record}",
        }

        headers = {
            "x-rapidapi-key": _ds.X_RAPIDAPI_KEY,
            "x-rapidapi-host": "linkmydeals.p.rapidapi.com",
        }

        response = requests.request(
            "GET", url, headers=headers, params=querystring
        ).json()

        # print(response.text)
        with open("data.json", "w") as data_file:
            json.dump(response, data_file, indent=4)

        return Response(response)


class UploadToTheDBView(generics.views.APIView):
    def get(self, request):
        count = 0
        added = 0

        with open("data.json") as data_file:
            data = json.load(data_file)

        offers_data = data.get("offers")

        if not offers_data:
            return KeyError("Can't find offers data...")

        for offer_data in offers_data:

            count += 1

            offer = Offer.objects.filter(lmd_id=offer_data["lmd_id"]).first()

            if offer:
                continue

            offer = Offer.objects.create(
                lmd_id=offer_data["lmd_id"],
                store=offer_data["store"],
                offer_text=offer_data["offer_text"],
                offer_value=offer_data["offer_value"],
                description=offer_data["description"],
                code=offer_data["code"] if offer_data["code"] else None,
                title=offer_data["title"],
                featured=(False if offer_data["featured"] == "No" else True),
                url=offer_data["url"],
                smart_link=offer_data["smartLink"],
                image_url=offer_data["image_url"],
                type=offer_data["type"],
                offer=offer_data["offer"],
                status=offer_data["status"],
                start_date=offer_data["start_date"],
                end_date=offer_data["end_date"],
            )

            categories = offer_data["categories"].split(',')

            for category_name in categories:
                category = Category.objects.filter(name=category_name).first()

                if category:
                    offer.categories.add(category)
                    continue

                category = Category.objects.create(name=category_name)
                offer.categories.add(category)

            added += 1

        return Response({"ok": True, "count": count, "added": added})
