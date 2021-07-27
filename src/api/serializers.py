from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Offer


class OfferSerializer(serializers.ModelSerializer):

    categories = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)

    class Meta:
        model = Offer
        fields = "__all__"
