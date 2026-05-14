from django.urls import path
from . import views

urlpatterns = [
    # Объявления (Listings)
    path('', views.ListingListCreateView.as_view(), name='listing-list'),
    path('my/', views.my_listings_view, name='my-listings'),
    path('search/', views.search_listings_view, name='search-listings'),
    path('popular/', views.popular_listings_view, name='popular-listings'),
    path('<int:pk>/', views.ListingDetailView.as_view(), name='listing-detail'),
    path('<int:pk>/toggle-status/', views.toggle_listing_status_view, name='toggle-listing-status'),
]
