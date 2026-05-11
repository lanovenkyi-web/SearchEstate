from django.urls import path
from . import views

urlpatterns = [
    # Основные CRUD операции
    path('', views.BookingListCreateView.as_view(), name='booking-list-create'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),

    # Персональные бронирования
    path('my/', views.my_bookings_view, name='my-bookings'),
    path('owner/', views.owner_bookings_view, name='owner-bookings'),

    # Управление статусами
    path('<int:pk>/confirm/', views.confirm_booking_view, name='confirm-booking'),
    path('<int:pk>/reject/', views.reject_booking_view, name='reject-booking'),
    path('<int:pk>/cancel/', views.cancel_booking_view, name='cancel-booking'),
]
