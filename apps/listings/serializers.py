from rest_framework import serializers
from .models import Estate, Listing, SearchHistory, ViewHistory


# OopCompanion:suppressRename


class ListingBaseSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='estate.title', read_only=True)
    description = serializers.CharField(source='estate.description', read_only=True)
    city = serializers.CharField(source='estate.city', read_only=True)
    district = serializers.CharField(source='estate.district', read_only=True)
    price = serializers.DecimalField(source='estate.price', max_digits=12, decimal_places=2, read_only=True)
    rooms = serializers.IntegerField(source='estate.rooms', read_only=True)
    housing_type = serializers.CharField(source='estate.housing_type', read_only=True)
    housing_type_display = serializers.CharField(source='estate.get_housing_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    owner_email = serializers.EmailField(source='estate.owner.email', read_only=True)


class ListingSerializer(ListingBaseSerializer):
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'city', 'district', 'price',
            'rooms', 'housing_type', 'housing_type_display',
            'status', 'status_display', 'views_count', 'owner_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'views_count', 'created_at', 'updated_at']


class ListingListSerializer(ListingBaseSerializer):
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'city', 'district', 'price',
            'rooms', 'housing_type', 'housing_type_display',
            'status', 'status_display', 'views_count', 'owner_email', 'created_at'
        ]


class ListingCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    rooms = serializers.IntegerField()
    housing_type = serializers.ChoiceField(choices=Estate.HOUSING_TYPES)
    city = serializers.CharField(max_length=100)
    district = serializers.CharField(max_length=100)

    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'rooms', 'housing_type', 'city', 'district']

    def validate(self, attrs):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if not request.user.is_staff and not request.user.is_landlord():
                raise serializers.ValidationError("Только арендодатель может создавать объявления")
        return attrs

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть положительной")
        return value

    def validate_rooms(self, value):
        if value < 1 or value > 50:
            raise serializers.ValidationError("Количество комнат должно быть от 1 до 50")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        estate = Estate.objects.create(owner=request.user, **validated_data)
        return Listing.objects.create(estate=estate, status=Listing.Status.ACTIVE)


class ListingUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    rooms = serializers.IntegerField(required=False)
    housing_type = serializers.ChoiceField(choices=Estate.HOUSING_TYPES, required=False)
    city = serializers.CharField(max_length=100, required=False)
    district = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = Listing
        fields = ['status', 'title', 'description', 'price', 'rooms', 'housing_type', 'city', 'district']

    def validate(self, attrs):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if not request.user.is_staff and not request.user.is_landlord():
                raise serializers.ValidationError("Только арендодатель может редактировать объявления")
        return attrs

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть положительной")
        return value

    def validate_rooms(self, value):
        if value < 1 or value > 50:
            raise serializers.ValidationError("Количество комнат должно быть от 1 до 50")
        return value

    def update(self, instance, validated_data):
        estate_fields = ['title', 'description', 'price', 'rooms', 'housing_type', 'city', 'district']
        estate_data = {field: validated_data.pop(field) for field in estate_fields if field in validated_data}

        for attr, value in estate_data.items():
            setattr(instance.estate, attr, value)
        if estate_data:
            instance.estate.save()

        return super().update(instance, validated_data)


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'query', 'search_count', 'last_searched_at', 'created_at']
        read_only_fields = ['id', 'search_count', 'last_searched_at', 'created_at']



class ViewHistorySerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.estate.title', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ViewHistory
        fields = ['id', 'listing', 'listing_title', 'user', 'user_email', 'viewed_at']
        read_only_fields = ['id', 'viewed_at']