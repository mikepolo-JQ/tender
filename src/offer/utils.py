from django_filters import rest_framework as filters

from offer.models import Offer


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class OfferFilter(filters.FilterSet):
    categories = CharFilterInFilter(field_name="categories__name", lookup_expr="in")
    types = CharFilterInFilter(field_name="types__name", lookup_expr="in")
    store = filters.CharFilter(field_name="store__name")
    start_date = filters.DateFilter(lookup_expr="gte")
    end_date = filters.DateFilter(lookup_expr="lte")

    class Meta:
        model = Offer
        fields = ["categories", "types", "store", "start_date", "end_date"]
