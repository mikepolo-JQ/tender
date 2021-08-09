from django_filters import rest_framework as filters
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

from applications.notification.models import Notification
from applications.offer.models import Offer, User
from applications.user_profile.serializers import UserListSerializer


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class OfferFilter(filters.FilterSet):
    categories = CharFilterInFilter(field_name="categories__name", lookup_expr="in")
    types = CharFilterInFilter(field_name="types__name", lookup_expr="in")
    store = filters.CharFilter(field_name="store__name")
    start_date = filters.DateFromToRangeFilter()
    end_date = filters.DateFromToRangeFilter()
    featured = filters.BooleanFilter()

    class Meta:
        model = Offer
        fields = ["categories", "types", "store", "start_date", "end_date", "featured"]


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow author of an object to edit it.
    Assumes the model instance has an `author` attribute.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


def user_offers_add_delete(self, request, **kwargs):
    user = self.request.user

    add_or_delete = {
        "add": user.offers.add,
        "delete": user.offers.remove
    }.get(kwargs.get("command"))

    try:
        offer = Offer.objects.get(pk=kwargs.get("pk"))
        add_or_delete(offer)

        return Response(status.HTTP_200_OK)
    except Offer.DoesNotExist:
        return Response(status.HTTP_404_NOT_FOUND)



