from django_filters import rest_framework as filters

from offer.models import Offer


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class OfferFilter(filters.FilterSet):
    categories = CharFilterInFilter(field_name="categories__name", lookup_expr="in")
    types = CharFilterInFilter(field_name="types__name", lookup_expr="in")

    class Meta:
        model = Offer
        fields = ["categories", "types", "store"]