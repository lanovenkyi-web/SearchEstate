from rest_framework import generics, status, permissions, filters, exceptions
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from .models import Booking
from .serializers import (
    BookingCreateSerializer, BookingListSerializer,
    BookingDetailSerializer, BookingUpdateSerializer
)
from apps.listings.models import Listing


# OopCompanion:suppressRename


class BookingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'listing', 'tenant']
    search_fields = ['listing__estate__title', 'listing__estate__city']
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        user = self.request.user
        queryset = Booking.objects.select_related('listing', 'listing__estate', 'listing__estate__owner', 'tenant')

        if user.is_staff:
            # Admin sees all bookings
            return queryset
        elif user.is_landlord():
            # Owner sees bookings for their properties
            return queryset.filter(listing__estate__owner=user)
        else:
            # Tenant sees their own bookings
            return queryset.filter(tenant=user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingListSerializer


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        user = self.request.user
        queryset = Booking.objects.select_related('listing', 'listing__estate', 'listing__estate__owner', 'tenant')

        if user.is_staff:
            return queryset
        elif user.is_landlord():
            return queryset.filter(listing__estate__owner=user)
        else:
            return queryset.filter(tenant=user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookingUpdateSerializer
        return BookingDetailSerializer

    def perform_destroy(self, instance):
        user = self.request.user

        # Only tenant can cancel their own booking
        if instance.tenant != user and not user.is_staff:
            raise exceptions.PermissionDenied("Вы можете отменить только свои бронирования")

        # Cannot delete confirmed booking
        if instance.status == 'confirmed':
            raise exceptions.PermissionDenied("Нельзя удалить подтвержденное бронирование")

        if instance.start_date <= timezone.localdate():
            raise exceptions.PermissionDenied("Бронирование можно отменить только до даты начала")

        listing = instance.listing
        instance.delete()

        other_confirmed_bookings = Booking.objects.filter(
            listing=listing,
            status='confirmed'
        )

        if not other_confirmed_bookings.exists():
            listing.status = Listing.Status.ACTIVE
            listing.save()


@extend_schema(responses=BookingListSerializer(many=True))
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_bookings_view(request):
    bookings = Booking.objects.filter(
        tenant=request.user
    ).select_related('listing', 'listing__estate', 'listing__estate__owner')

    status_filter = request.query_params.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    serializer = BookingListSerializer(bookings, many=True)
    return Response(serializer.data)


@extend_schema(responses=BookingListSerializer(many=True))
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def owner_bookings_view(request):
    if not request.user.is_landlord() and not request.user.is_staff:
        return Response(
            {'error': 'У вас нет прав для просмотра бронирований'},
            status=status.HTTP_403_FORBIDDEN
        )

    bookings = Booking.objects.filter(
        listing__estate__owner=request.user
    ).select_related('listing', 'listing__estate', 'tenant')

    status_filter = request.query_params.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    serializer = BookingListSerializer(bookings, many=True)
    return Response(serializer.data)


@extend_schema(methods=['POST'], request=None, responses=BookingDetailSerializer)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_booking_view(request, pk):
    try:
        booking = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        return Response({'error': 'Бронирование не найдено'}, status=status.HTTP_404_NOT_FOUND)

    # Permission check (only property owner can confirm)
    if booking.listing.estate.owner != request.user and not request.user.is_staff:
        return Response(
            {'error': 'У вас нет прав для подтверждения этого бронирования'},
            status=status.HTTP_403_FORBIDDEN
        )

    if booking.status != 'new':
        return Response(
            {'error': 'Можно подтвердить только новые бронирования'},
            status=status.HTTP_400_BAD_REQUEST
        )

    booking.status = 'confirmed'
    booking.save()

    # Update listing status
    booking.listing.status = Listing.Status.BOOKED
    booking.listing.save()

    serializer = BookingDetailSerializer(booking)
    return Response(serializer.data)


@extend_schema(methods=['POST'], request=None, responses=BookingDetailSerializer)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_booking_view(request, pk):
    try:
        booking = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        return Response({'error': 'Бронирование не найдено'}, status=status.HTTP_404_NOT_FOUND)

    # Permission check (only property owner can reject)
    if booking.listing.estate.owner != request.user and not request.user.is_staff:
        return Response(
            {'error': 'У вас нет прав для отклонения этого бронирования'},
            status=status.HTTP_403_FORBIDDEN
        )

    if booking.status != 'new':
        return Response(
            {'error': 'Можно отклонить только новые бронирования'},
            status=status.HTTP_400_BAD_REQUEST
        )

    booking.status = 'rejected'
    booking.save()

    other_confirmed_bookings = Booking.objects.filter(
        listing=booking.listing,
        status='confirmed'
    ).exclude(pk=booking.pk)

    if not other_confirmed_bookings.exists():
        booking.listing.status = Listing.Status.ACTIVE
        booking.listing.save()

    serializer = BookingDetailSerializer(booking)
    return Response(serializer.data)


@extend_schema(methods=['POST'], request=None, responses=BookingDetailSerializer)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_booking_view(request, pk):
    try:
        booking = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        return Response({'error': 'Бронирование не найдено'}, status=status.HTTP_404_NOT_FOUND)

    # Permission check (only tenant can cancel)
    if booking.tenant != request.user and not request.user.is_staff:
        return Response(
            {'error': 'У вас нет прав для отмены этого бронирования'},
            status=status.HTTP_403_FORBIDDEN
        )

    if booking.status == 'canceled':
        return Response(
            {'error': 'Бронирование уже отменено'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if booking.status == 'confirmed':
        return Response(
            {'error': 'Нельзя отменить подтвержденное бронирование'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if booking.start_date <= timezone.localdate():
        return Response(
            {'error': 'Бронирование можно отменить только до даты начала'},
            status=status.HTTP_400_BAD_REQUEST
        )

    booking.status = 'canceled'
    booking.save()

    other_confirmed_bookings = Booking.objects.filter(
        listing=booking.listing,
        status='confirmed'
    ).exclude(pk=booking.pk)

    if not other_confirmed_bookings.exists():
        booking.listing.status = Listing.Status.ACTIVE
        booking.listing.save()

    serializer = BookingDetailSerializer(booking)
    return Response(serializer.data)
