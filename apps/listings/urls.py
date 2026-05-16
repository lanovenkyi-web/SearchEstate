from django.urls import path
from . import views
from .views import popular_searches_view, my_view_history_view, listing_view_history_view

urlpatterns = [
    # Объявления (Listings)
    path('', views.ListingListCreateView.as_view(), name='listing-list'),
    path('my/', views.my_listings_view, name='my-listings'),
    path('search/', views.search_listings_view, name='search-listings'),
    path('popular/', views.popular_listings_view, name='popular-listings'),
    path('<int:pk>/', views.ListingDetailView.as_view(), name='listing-detail'),
    path('<int:pk>/toggle-status/', views.toggle_listing_status_view, name='toggle-listing-status'),
    path('popular-searches/', popular_searches_view, name='popular-searches'),
    # История просмотров
    path('my-view-history/', my_view_history_view, name='my-view-history'),
    path('<int:pk>/view-history/', listing_view_history_view, name='listing-view-history'),
]
