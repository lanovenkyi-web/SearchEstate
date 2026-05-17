import django_filters
from .models import Estate, Listing


# OopCompanion:suppressRename

class ListingFilter(django_filters.FilterSet):
    """Filter for listings.
    
    Allows filtering listings by price, number of rooms,
    housing type, location, status, owner, and creation date.
    """
    min_price = django_filters.NumberFilter(field_name='estate__price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='estate__price', lookup_expr='lte')
    min_rooms = django_filters.NumberFilter(field_name='estate__rooms', lookup_expr='gte')
    max_rooms = django_filters.NumberFilter(field_name='estate__rooms', lookup_expr='lte')
    housing_type = django_filters.ChoiceFilter(field_name='estate__housing_type', choices=Estate.HOUSING_TYPES)
    city = django_filters.CharFilter(field_name='estate__city', lookup_expr='icontains')
    district = django_filters.CharFilter(field_name='estate__district', lookup_expr='icontains')
    estate = django_filters.NumberFilter(field_name='estate_id')
    status = django_filters.ChoiceFilter(choices=Listing.Status.choices)
    owner = django_filters.NumberFilter(field_name='estate__owner_id')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Listing
        fields = ['estate', 'status', 'owner']
