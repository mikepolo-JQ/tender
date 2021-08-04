from rest_framework import serializers
from applications.offer.models import Offer, Store, Review
from applications.user_profile.serializers import UserListSerializer


class OfferListSerializer(serializers.ModelSerializer):

    store = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Offer
        fields = ["id", "title", "rating", "store"]


class StoreListSerializer(serializers.ModelSerializer):

    offers = OfferListSerializer(many=True)

    class Meta:
        model = Store
        fields = ["id", "name", "description", "rating", "offers"]


class StoreLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "name"]


class OfferDetailSerializer(serializers.ModelSerializer):

    categories = serializers.SlugRelatedField(
        slug_field="name", read_only=True, many=True
    )
    types = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    store = StoreLightSerializer()

    class Meta:
        model = Offer
        fields = "__all__"


class StoreDetailSerializer(serializers.ModelSerializer):

    offers = OfferDetailSerializer(many=True)

    class Meta:
        model = Store
        fields = "__all__"


class RecursiveSerializer(serializers.Serializer):
    """Recursively output the children of the object"""

    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data


class FilterReviewListSerializer(serializers.ListSerializer):
    """Reviews filter output only parents"""

    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class ReviewListSerializer(serializers.ModelSerializer):
    author = UserListSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    rating_value = serializers.IntegerField(min_value=0, max_value=5)
    children = RecursiveSerializer(many=True, read_only=True)

    def get_likes_count(self, review):
        return review.likers.count()

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Review
        exclude = ["likers", "object_id", "parent", "content_type"]


class ReviewDetailSerializer(serializers.ModelSerializer):
    author = UserListSerializer()
    likers = UserListSerializer(many=True)
    content_type = serializers.SlugRelatedField(slug_field="name", read_only=True)
    owner = serializers.SerializerMethodField()
    rating_value = serializers.IntegerField(min_value=0, max_value=5)

    def get_owner(self, review):
        try:
            owner_names_dict = {
                "store": StoreListSerializer(
                    Store.objects.get(pk=review.owner.pk)
                ).data,
                "offer": OfferListSerializer(
                    Offer.objects.get(pk=review.owner.pk)
                ).data,
            }
        except Store.DoesNotExist:
            return OfferListSerializer(Offer.objects.get(pk=review.owner.pk)).data
        return owner_names_dict[review.content_type.name]

    class Meta:
        model = Review
        exclude = ["object_id", "parent"]
