import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):

    sent_at = django_filters.DateFromToRangeFilter()

    participant = django_filters.DateTimeFromToRangeFilter(
        field_name='conversation__participants'
    )
    class Meta:
        model = Message
        fields = ['sent_at', 'participant','conversation',]