from rest_framework import generics, permissions, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from .models import Review
from .serializers import (
    ReviewCreateSerializer, ReviewListSerializer,
    ReviewDetailSerializer, ReviewUpdateSerializer
)


# OopCompanion:suppressRename


class ReviewListCreateView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['listing', 'author', 'rating']
    search_fields = ['listing__estate__title', 'listing__estate__city', 'text']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = Review.objects.select_related('listing', 'listing__estate', 'listing__estate__owner', 'author')

        # Фильтрация по объекту
        listing_id = self.request.query_params.get('listing_id')
        if listing_id:
            queryset = queryset.filter(listing_id=listing_id)

        # Фильтрация по автору
        author_id = self.request.query_params.get('author_id')
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        # Фильтрация по рейтингу
        min_rating = self.request.query_params.get('min_rating')
        max_rating = self.request.query_params.get('max_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        if max_rating:
            queryset = queryset.filter(rating__lte=max_rating)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewListSerializer


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.select_related('listing', 'listing__estate', 'listing__estate__owner', 'author')

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ReviewUpdateSerializer
        return ReviewDetailSerializer

    def perform_update(self, serializer):
        # Только автор может редактировать свой отзыв
        if serializer.instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Вы можете редактировать только свои отзывы")
        serializer.save()

    def perform_destroy(self, instance):
        # Только автор может удалить свой отзыв
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Вы можете удалять только свои отзывы")
        instance.delete()


@extend_schema(responses=ReviewListSerializer(many=True))
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_reviews_view(request):
    reviews = Review.objects.filter(
        author=request.user
    ).select_related('listing', 'listing__estate', 'listing__estate__owner')

    rating_filter = request.query_params.get('rating')
    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)

    serializer = ReviewListSerializer(reviews, many=True)
    return Response(serializer.data)


@extend_schema(responses=ReviewListSerializer(many=True))
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def listing_reviews_view(request, pk):
    reviews = Review.objects.filter(
        listing_id=pk
    ).select_related('author', 'listing', 'listing__estate', 'listing__estate__owner')

    serializer = ReviewListSerializer(reviews, many=True)
    return Response(serializer.data)

