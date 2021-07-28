import json

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from offer.models import Offer, Store, Review


class OfferSerializer(serializers.ModelSerializer):

    categories = serializers.SlugRelatedField(
        slug_field="name", read_only=True, many=True
    )
    types = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    store = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Offer
        fields = "__all__"


class StoreSerializer(serializers.ModelSerializer):

    # offers = OfferSerializer(many=True)

    class Meta:
        model = Store
        fields = ["id", "name", "description", "rating", "offers"]


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("content", "rating_value")


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    likes_count = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_likes_count(self, review):
        return review.likers.count()

    def get_owner(self, review):

        owner_names_dict = {
            "store": StoreSerializer(Store.objects.get(pk=review.owner.pk)).data,
            "offer": OfferSerializer(Offer.objects.get(pk=review.owner.pk)).data,
        }
        return owner_names_dict[review.content_type.name]

    class Meta:
        model = Review
        fields = ("id", "content", "rating_value", "author", "likes_count", "owner")
