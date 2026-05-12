from rest_framework import generics, status, permissions, filters
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Listing
from .serializers import (
    ListingSerializer, ListingCreateSerializer, ListingListSerializer,
    ListingUpdateSerializer
)
from .filters import ListingFilter


# OopCompanion:suppressRename


class ListingListCreateView(generics.ListCreateAPIView):
    queryset = Listing.objects.select_related('estate', 'estate__owner')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['estate__title', 'estate__description', 'estate__city']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'estate__price']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListingCreateSerializer
        return ListingListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listing = serializer.save()
        return Response(ListingSerializer(listing).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = Listing.objects.select_related('estate', 'estate__owner')

        if not self.request.user.is_staff:
            queryset = queryset.filter(status=Listing.Status.ACTIVE)

        owner_id = self.request.query_params.get('owner_id')
        if owner_id:
            queryset = queryset.filter(estate__owner_id=owner_id)

        cities = self.request.query_params.getlist('cities')
        if cities:
            queryset = queryset.filter(estate__city__in=cities)

        housing_types = self.request.query_params.getlist('housing_types')
        if housing_types:
            queryset = queryset.filter(estate__housing_type__in=housing_types)

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(estate__price__gte=min_price)
        if max_price:
            queryset = queryset.filter(estate__price__lte=max_price)

        return queryset


class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Listing.objects.select_related('estate', 'estate__owner')

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = Listing.objects.select_related('estate', 'estate__owner')
        user = self.request.user

        if not user.is_authenticated:
            return queryset.filter(status=Listing.Status.ACTIVE)
        if user.is_staff:
            return queryset
        return queryset.filter(Q(status=Listing.Status.ACTIVE) | Q(estate__owner=user))

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ListingUpdateSerializer
        return ListingSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        instance.views_count += 1
        instance.save(update_fields=['views_count'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.estate.owner != request.user and not request.user.is_staff:
            raise PermissionDenied("Вы можете редактировать только свои объявления")

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        listing = serializer.save()
        return Response(ListingSerializer(listing).data)

    def perform_update(self, serializer):

        if serializer.instance.estate.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Вы можете редактировать только свои объявления")
        serializer.save()

    def perform_destroy(self, instance):

        if instance.estate.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Вы можете удалять только свои объявления")
        instance.delete()


@extend_schema(responses=ListingListSerializer(many=True))
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_listings_view(request):
    listings = Listing.objects.filter(
        estate__owner=request.user
    ).select_related('estate', 'estate__owner')
    serializer = ListingListSerializer(listings, many=True)
    return Response(serializer.data)


@extend_schema(methods=['POST'], request=None, responses=ListingSerializer)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_listing_status_view(request, pk):
    try:
        listing = Listing.objects.get(pk=pk)
    except Listing.DoesNotExist:
        return Response({'error': 'Объявление не найдено'}, status=status.HTTP_404_NOT_FOUND)

    if listing.estate.owner != request.user and not request.user.is_staff:
        return Response(
            {'error': 'У вас нет прав для изменения этого объявления'},
            status=status.HTTP_403_FORBIDDEN
        )

    if listing.status == Listing.Status.ACTIVE:
        listing.status = Listing.Status.ARCHIVED
    elif listing.status == Listing.Status.ARCHIVED:
        listing.status = Listing.Status.ACTIVE
    else:
        return Response(
            {'error': 'Нельзя изменить статус забронированного объявления'},
            status=status.HTTP_400_BAD_REQUEST
        )

    listing.save()
    serializer = ListingSerializer(listing)
    return Response(serializer.data)


@extend_schema(
    summary="Поиск объявлений",
    description="Ищет объявления по заголовку, описанию, городу или району.",
    parameters=[
        OpenApiParameter(
            name='q',
            description='Текст для поиска (мин. 1 символ)',
            required=True,
            type=str
        ),
    ],
    responses=inline_serializer(
        name='ListingSearchResponse',
        fields={
            'found_count': serializers.IntegerField(),
            'results': ListingListSerializer(many=True),
        },
    )
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_listings_view(request):
    query = request.query_params.get('q', '')

    if not query:
        return Response(
            {'error': 'Параметр поиска обязателен'},
            status=status.HTTP_400_BAD_REQUEST
        )

    listings_query = Listing.objects.filter(
        Q(estate__title__icontains=query) |
        Q(estate__description__icontains=query) |
        Q(estate__city__icontains=query) |
        Q(estate__district__icontains=query)
    ).select_related('estate', 'estate__owner')

    if not request.user.is_authenticated or not request.user.is_staff:
        listings_query = listings_query.filter(status=Listing.Status.ACTIVE)

    serializer = ListingListSerializer(listings_query, many=True)
    return Response({
        'found_count': listings_query.count(),
        'results': serializer.data
    })


@extend_schema(responses=ListingListSerializer(many=True))
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def popular_listings_view(request):
    listings = Listing.objects.filter(
        status=Listing.Status.ACTIVE
    ).select_related('estate', 'estate__owner').order_by('-views_count')[:10]

    serializer = ListingListSerializer(listings, many=True)
    return Response(serializer.data)

