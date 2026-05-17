from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    #Authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.login_view, name='user-login'),
    path('logout/', views.logout_view, name='user-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    #User profile
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('current/', views.current_user_view, name='current-user'),
    path('change-password/', views.change_password_view, name='change-password'),
]
