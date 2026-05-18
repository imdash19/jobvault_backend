"""
JobVault Backend — Root URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication — register, login, logout, profile, token refresh
    path('api/auth/', include('accounts.urls')),

    # Job Applications — CRUD + Dashboard
    path('api/', include('applications.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
