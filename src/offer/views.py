import json

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
import requests
from dynaconf import settings as _ds

from rest_framework.response import Response

from offer.models import Offer, Category, Type, Store, Review
from offer import serializers
from offer.service import OfferFilter, IsOwnerOrReadOnly


class OfferListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]

    model = Offer
    queryset = Offer.objects.all()
    serializer_class = serializers.OfferSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OfferFilter


class OfferDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]

    model = Offer
    queryset = Offer.objects.filter()
    serializer_class = serializers.OfferSerializer


class OwnerReviewsListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    model = Review
    serializer_class = serializers.ReviewSerializer

    def get_owner_class(self):
        class_name = self.request.path.split("/")[2]
        owner_class = {"offer": Offer, "store": Store}.get(class_name)

        if not owner_class:
            raise KeyError("Owner class for this review list isn't found.")

        return owner_class

    def get_queryset(self):
        owner_class = self.get_owner_class()

        pk = self.kwargs.get("pk")
        queryset = owner_class.objects.get(pk=pk).reviews.all()
        return queryset

    def perform_create(self, serializer):
        owner_class = self.get_owner_class()

        pk = self.kwargs.get("pk")
        owner = owner_class.objects.get(pk=pk)
        user = self.request.user

        serializer.save(author_id=user.pk, owner=owner)

        owner.update_rating()


# //////////////////////// STORE ///////////////////////////////
class StoreListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]

    model = Store
    queryset = Store.objects.all()
    serializer_class = serializers.StoreSerializer
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = OfferFilter


class StoreDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]

    model = Store
    queryset = Store.objects.filter()
    serializer_class = serializers.StoreSerializer


# //////////////////////// REVIEWS ///////////////////////////////
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    model = Review
    serializer_class = serializers.ReviewSerializer
    queryset = Review.objects.filter()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_destroy(self, instance):
        instance.owner.update_rating()
        super().perform_destroy(instance)

    def perform_update(self, serializer):
        super().perform_update(serializer)

        review = self.get_object()
        review.owner.update_rating()


class ReviewLikeView(generics.views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        pk = kwargs["pk"]

        review = Review.objects.filter(pk=pk).first()

        if not review:
            raise ModuleNotFoundError(f"Review with pk={pk} is not found")

        if review.likers.filter(pk=user.pk).exists():
            review.likers.remove(user.pk)
        else:
            review.likers.add(user)
        return Response({"ok": True})


# //////////////////////// ADMIN ///////////////////////////////
class DataUpdateView(generics.views.APIView):

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):

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

        with open("data.json", "w") as data_file:
            json.dump(response, data_file, indent=4)

        return Response(response)


class UploadToTheDBView(generics.views.APIView):

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
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

            # adding stores
            store_name = offer_data["store"]

            store = Store.objects.filter(name=store_name).first()

            if not store:
                store = Store.objects.create(name=store_name)

            # creature offers
            offer = Offer.objects.create(
                lmd_id=offer_data["lmd_id"],
                store=store,
                offer_text=offer_data["offer_text"],
                offer_value=offer_data["offer_value"],
                description=offer_data["description"],
                code=offer_data["code"] if offer_data["code"] else None,
                title=offer_data["title"],
                featured=(False if offer_data["featured"] == "No" else True),
                url=offer_data["url"],
                smart_link=offer_data["smartLink"],
                image_url=offer_data["image_url"],
                status=offer_data["status"],
                start_date=offer_data["start_date"],
                end_date=offer_data["end_date"],
            )

            # adding categories
            categories = offer_data["categories"].split(",")

            for category_name in categories:
                category = Category.objects.filter(name=category_name).first()

                if not category:
                    category = Category.objects.create(name=category_name)

                offer.categories.add(category)

            # adding types
            types = [offer_data["type"], offer_data["offer"]]

            for type_name in types:
                type_obj = Type.objects.filter(name=type_name).first()

                if not type_obj:
                    type_obj = Type.objects.create(name=type_name)

                offer.types.add(type_obj)

            added += 1

        return Response({"ok": True, "count": count, "added": added})
