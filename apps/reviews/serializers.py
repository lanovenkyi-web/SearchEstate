from rest_framework import serializers
from .models import Review
from apps.bookings.models import Booking


# OopCompanion:suppressRename

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['listing', 'rating', 'text']

    def validate_listing(self, value):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Check that user is not the owner
            if value.estate.owner == request.user:
                raise serializers.ValidationError("Вы не можете оставлять отзывы на свои объекты")

            # Check for confirmed booking
            has_confirmed_booking = Booking.objects.filter(
                listing=value,
                tenant=request.user,
                status='confirmed'
            ).exists()

            if not has_confirmed_booking:
                raise serializers.ValidationError("Вы можете оставить отзыв только после подтвержденного бронирования")

            # Check that user hasn't already reviewed this property
            existing_review = Review.objects.filter(
                listing=value,
                author=request.user
            ).exists()

            if existing_review:
                raise serializers.ValidationError("Вы уже оставили отзыв на этот объект")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)


class ReviewListSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)
    listing_title = serializers.CharField(source='listing.estate.title', read_only=True)
    listing_city = serializers.CharField(source='listing.estate.city', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'listing_title', 'listing_city',
            'author_email', 'rating', 'created_at'
        ]


class ReviewDetailSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_role = serializers.CharField(source='author.get_role_display', read_only=True)
    listing_title = serializers.CharField(source='listing.estate.title', read_only=True)
    listing_description = serializers.CharField(source='listing.estate.description', read_only=True)
    listing_city = serializers.CharField(source='listing.estate.city', read_only=True)
    listing_district = serializers.CharField(source='listing.estate.district', read_only=True)
    listing_price = serializers.DecimalField(source='listing.estate.price', max_digits=12, decimal_places=2,
                                             read_only=True)
    listing_housing_type = serializers.CharField(source='listing.estate.get_housing_type_display', read_only=True)
    owner_email = serializers.EmailField(source='listing.estate.owner.email', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'listing', 'listing_title', 'listing_description',
            'listing_city', 'listing_district', 'listing_price',
            'listing_housing_type',
            'author', 'author_email', 'author_role',
            'owner_email', 'rating', 'text', 'created_at'
        ]
        read_only_fields = ['id', 'author', 'created_at']


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'text']

    def validate(self, attrs):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Only author can edit their review
            if self.instance.author != request.user and not request.user.is_staff:
                raise serializers.ValidationError("Только автор может редактировать свой отзыв")

        return attrs
