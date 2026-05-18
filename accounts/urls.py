"""
accounts/urls.py
────────────────────────────────────────────────────────────────────
Auth Endpoints:

  POST   /api/auth/register/          — new user registration
  POST   /api/auth/login/             — obtain access + refresh tokens
  POST   /api/auth/logout/            — blacklist refresh token
  POST   /api/auth/token/refresh/     — get new access token via refresh
  GET    /api/auth/profile/           — get current user profile
  PATCH  /api/auth/profile/           — update profile (name, email)
  POST   /api/auth/change-password/   — change password
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView, ProfileView, LogoutView, ChangePasswordView

urlpatterns = [
    # Registration
    path('register/', RegisterView.as_view(), name='auth-register'),

    # JWT Login — returns {"access": "...", "refresh": "..."}
    path('login/', TokenObtainPairView.as_view(), name='auth-login'),

    # JWT Token Refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),

    # Logout — blacklists refresh token
    path('logout/', LogoutView.as_view(), name='auth-logout'),

    # User Profile
    path('profile/', ProfileView.as_view(), name='auth-profile'),

    # Change Password
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
]
