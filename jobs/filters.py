import django_filters
from django.db import models

from .models import Job


class JobFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_search", label="Search")
    mode = django_filters.ChoiceFilter(choices=Job.Mode.choices, label="Mode")
    status = django_filters.ChoiceFilter(choices=Job.Status.choices, label="Status")

    class Meta:
        model = Job
        fields = ["mode", "status"]

    def filter_search(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                models.Q(title__icontains=value)
                | models.Q(description__icontains=value)
                | models.Q(subject__icontains=value)
            )
        return queryset
