"""
applications/urls.py
────────────────────────────────────────────────────────────────────
Application Endpoints:

  CRUD (via DefaultRouter):
    GET    /api/applications/           list all applications (own)
    POST   /api/applications/           create new application
    GET    /api/applications/{id}/      get single application
    PUT    /api/applications/{id}/      full update
    PATCH  /api/applications/{id}/      partial update
    DELETE /api/applications/{id}/      delete

  Dashboard:
    GET    /api/dashboard/stats/        overall counts
    GET    /api/dashboard/monthly/      monthly trend (last 12 months)
    GET    /api/dashboard/platform/     breakdown by platform
    GET    /api/dashboard/status/       breakdown by status

Query Parameters (for list endpoint):
  Filtering : ?status=Applied  ?applied_platform=LinkedIn
              ?applied_date=2024-06-01
              ?applied_date_from=2024-01-01&applied_date_to=2024-06-30
  Searching : ?search=Google
  Ordering  : ?ordering=-applied_date  ?ordering=company_name
  Pagination: ?page=2
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ApplicationViewSet,
    DashboardStatsView,
    DashboardMonthlyView,
    DashboardPlatformView,
    DashboardStatusView,
)

# ── Router for ApplicationViewSet ──────────────────────────────────────────────
router = DefaultRouter()
router.register(r'applications', ApplicationViewSet, basename='application')

urlpatterns = [
    # CRUD
    path('', include(router.urls)),

    # Dashboard
    path('dashboard/stats/',    DashboardStatsView.as_view(),    name='dashboard-stats'),
    path('dashboard/monthly/',  DashboardMonthlyView.as_view(),  name='dashboard-monthly'),
    path('dashboard/platform/', DashboardPlatformView.as_view(), name='dashboard-platform'),
    path('dashboard/status/',   DashboardStatusView.as_view(),   name='dashboard-status'),
]
