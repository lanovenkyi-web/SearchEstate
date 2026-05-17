from rest_framework import serializers
from django.utils import timezone
from .models import Booking
from apps.listings.models import Listing


# OopCompanion:suppressRename

class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a booking.
    
    Validates user permissions, date validity, and absence of overlaps.
    """

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'start_date', 'end_date']
        read_only_fields = ['id']

    def validate_listing(self, value):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if not request.user.is_tenant() and not request.user.is_staff:
                raise serializers.ValidationError("Бронировать жилье может только арендатор")

            # Check that user is not the owner
            if value.estate.owner == request.user:
                raise serializers.ValidationError("Вы не можете бронировать свои объекты")

            # Check that the listing is active
            if value.status != Listing.Status.ACTIVE:
                raise serializers.ValidationError("Можно бронировать только активные объявления")
        return value

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        listing = attrs.get('listing')

        if end_date <= start_date:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала")

        if start_date < timezone.localdate():
            raise serializers.ValidationError("Нельзя создать бронирование на прошедшую дату")

        conflicting_bookings = Booking.objects.filter(
            listing=listing,
            status__in=['new', 'confirmed'],
            start_date__lte=end_date,
            end_date__gte=start_date,
        )
        if conflicting_bookings.exists():
            raise serializers.ValidationError("Объект уже забронирован на эти даты")

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['tenant'] = request.user
        return super().create(validated_data)


class BookingListSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.estate.title', read_only=True)
    listing_city = serializers.CharField(source='listing.estate.city', read_only=True)
    listing_price = serializers.DecimalField(source='listing.estate.price', max_digits=12, decimal_places=2,
                                             read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    owner_email = serializers.EmailField(source='listing.estate.owner.email', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'listing_title', 'listing_city', 'listing_price',
            'start_date', 'end_date', 'status_display', 'owner_email'
        ]


class BookingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['status']

    def validate_status(self, value):
        request = self.context.get('request')
        booking = self.instance

        if request and hasattr(request, 'user'):
            # Only owner can confirm or reject booking
            if value in ['confirmed', 'rejected']:
                if booking.listing.estate.owner != request.user and not request.user.is_staff:
                    raise serializers.ValidationError(
                        "Только владелец объекта может подтвердить или отклонить бронирование")

            # Only tenant can cancel booking
            elif value == 'canceled':
                if booking.tenant != request.user and not request.user.is_staff:
                    raise serializers.ValidationError("Только арендатор может отменить бронирование")

                if booking.start_date <= timezone.localdate():
                    raise serializers.ValidationError("Бронирование можно отменить только до даты начала")

                # Cannot cancel confirmed booking
                if booking.status == 'confirmed':
                    raise serializers.ValidationError("Нельзя отменить подтвержденное бронирование")

        return value


class BookingDetailSerializer(serializers.ModelSerializer):
    tenant_email = serializers.EmailField(source='tenant.email', read_only=True)
    tenant_phone = serializers.CharField(source='tenant.phone_number', read_only=True)
    listing_title = serializers.CharField(source='listing.estate.title', read_only=True)
    listing_description = serializers.CharField(source='listing.estate.description', read_only=True)
    listing_city = serializers.CharField(source='listing.estate.city', read_only=True)
    listing_district = serializers.CharField(source='listing.estate.district', read_only=True)
    listing_price = serializers.DecimalField(source='listing.estate.price', max_digits=12, decimal_places=2,
                                             read_only=True)
    listing_housing_type = serializers.CharField(source='listing.estate.get_housing_type_display', read_only=True)
    listing_rooms = serializers.IntegerField(source='listing.estate.rooms', read_only=True)
    owner_email = serializers.EmailField(source='listing.estate.owner.email', read_only=True)
    owner_phone = serializers.CharField(source='listing.estate.owner.phone_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_title', 'listing_description',
            'listing_city', 'listing_district', 'listing_price',
            'listing_housing_type', 'listing_rooms',
            'tenant', 'tenant_email', 'tenant_phone',
            'owner_email', 'owner_phone',
            'start_date', 'end_date', 'status', 'status_display'
        ]
