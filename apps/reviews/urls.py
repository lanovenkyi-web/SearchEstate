from django.urls import path
from . import views

urlpatterns = [
    # Основные CRUD операции
    path('', views.ReviewListCreateView.as_view(), name='review-list-create'),

    # Персональные отзывы
    path('my/', views.my_reviews_view, name='my-reviews'),

    # Отзывы для конкретного объявления
    path('listing/<int:pk>/', views.listing_reviews_view, name='listing-reviews'),
    # Детальный отзыв
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
]
