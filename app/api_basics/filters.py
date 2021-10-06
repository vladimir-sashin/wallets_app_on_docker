import django_filters

from .models import TransactionV2


class HistoryFilter(django_filters.rest_framework.FilterSet):
    transaction_type = django_filters.ChoiceFilter(
        choices=TransactionV2.TRANSACTION_TYPES_CHOICES
    )
    timestamp = django_filters.DateFromToRangeFilter()

    class Meta:
        model = TransactionV2
        fields = ["transaction_type", "timestamp"]
