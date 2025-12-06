import django_filters
from django.db import models

from .models import Listing


class ListingFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_search", label="Search")
    min = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte", label="Min Price"
    )
    max = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte", label="Max Price"
    )

    class Meta:
        model = Listing
        fields = ["price"]

    def filter_search(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                models.Q(title__icontains=value)
                | models.Q(description__icontains=value)
                | models.Q(subject__icontains=value)
                | models.Q(category__icontains=value)
            )
        return queryset
