
from rest_framework import serializers
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

    offers = OfferSerializer(many=True)

    class Meta:
        model = Store
        fields = ["id", "name", "description", "rating", "offers"]


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    likes_count = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    rating_value = serializers.IntegerField(min_value=0, max_value=5)

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
        fields = ("id", "content", "rating_value", "author", "likes_count", "owner", "created_at", "updated_at")
