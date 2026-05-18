"""
applications/permissions.py
────────────────────────────────────────────────────────────────────
Custom DRF permission:
  • IsOwner — the requesting user must be the owner of the object.

Usage:
    permission_classes = [IsAuthenticated, IsOwner]
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Object-level permission: only the owner of a JobApplication can access it.

    Assumes the model instance has a `user` attribute pointing to the owner.
    """

    message = "You do not have permission to access this application."

    def has_object_permission(self, request, view, obj):
        # Allow if the requesting user is the owner
        return obj.user == request.user
