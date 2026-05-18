"""
accounts/views.py
────────────────────────────────────────────────────────────────────
Views:
  • RegisterView        — POST  /api/auth/register/
  • ProfileView         — GET   /api/auth/profile/
                          PATCH /api/auth/profile/
  • LogoutView          — POST  /api/auth/logout/   (blacklists refresh token)
  • ChangePasswordView  — POST  /api/auth/change-password/

Token endpoints (from SimpleJWT):
  • LoginView           — POST  /api/auth/login/    (returns access + refresh)
  • TokenRefreshView    — POST  /api/auth/token/refresh/
"""

from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
)


# ─── Register ─────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/

    Creates a new user account.

    Request body:
        {
            "username": "johndoe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "StrongPass@123",
            "confirm_password": "StrongPass@123"
        }

    Response 201:
        {
            "message": "Account created successfully.",
            "user": { "id": 1, "username": "johndoe", ... }
        }
    """

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Optionally return tokens immediately on registration
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Account created successfully.",
                "user": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ─── Profile ──────────────────────────────────────────────────────────────────

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/auth/profile/   — returns current user data
    PATCH /api/auth/profile/   — updates first_name, last_name, email

    Response 200:
        { "id": 1, "username": "johndoe", "email": "john@example.com", ... }
    """

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProfileUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user

    # Override to always return full user data after update
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True   # always allow partial update
        response = super().update(request, *args, **kwargs)
        # Return full profile view after update
        response.data = UserSerializer(self.request.user).data
        return response


# ─── Logout ───────────────────────────────────────────────────────────────────

class LogoutView(APIView):
    """
    POST /api/auth/logout/

    Blacklists the provided refresh token, invalidating the session.

    Request body:
        { "refresh": "<refresh_token_string>" }

    Response 205:
        { "message": "Logged out successfully." }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (TokenError, InvalidToken) as e:
            return Response(
                {"error": "Invalid or expired token.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"message": "Logged out successfully."},
            status=status.HTTP_205_RESET_CONTENT,
        )


# ─── Change Password ──────────────────────────────────────────────────────────

class ChangePasswordView(APIView):
    """
    POST /api/auth/change-password/

    Changes the authenticated user's password.

    Request body:
        {
            "old_password": "CurrentPass@123",
            "new_password": "NewStrongPass@456",
            "confirm_new_password": "NewStrongPass@456"
        }

    Response 200:
        { "message": "Password changed successfully." }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )
