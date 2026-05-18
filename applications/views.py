"""
applications/views.py
────────────────────────────────────────────────────────────────────
Views:

  ApplicationViewSet   — Full CRUD for job applications
    GET    /api/applications/           list all (own)
    POST   /api/applications/           create new
    GET    /api/applications/{id}/      retrieve one
    PUT    /api/applications/{id}/      full update
    PATCH  /api/applications/{id}/      partial update
    DELETE /api/applications/{id}/      delete

  Dashboard views (all scoped to request.user):
    GET    /api/dashboard/stats/        overall counts
    GET    /api/dashboard/monthly/      monthly trend (last 12 months)
    GET    /api/dashboard/platform/     count by platform
    GET    /api/dashboard/status/       count by status
"""

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend

from .models import JobApplication, ApplicationStatus, AppliedPlatform
from .serializers import JobApplicationSerializer
from .permissions import IsOwner
from .filters import ApplicationFilter


# ─── Application ViewSet ──────────────────────────────────────────────────────

class ApplicationViewSet(viewsets.ModelViewSet):
    """
    Full CRUD ViewSet for JobApplication.

    Security:
        • IsAuthenticated — JWT required
        • IsOwner         — users can only touch their own records

    Filtering (?status=, ?applied_platform=, ?applied_date=, ?applied_date_from=, ?applied_date_to=):
        Uses ApplicationFilter (django-filter)

    Searching (?search=):
        Searches across company_name and job_role

    Ordering (?ordering=):
        Default: -applied_date, -created_at
        Available: applied_date, created_at, company_name, status
    """

    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ApplicationFilter
    search_fields = ['company_name', 'job_role']
    ordering_fields = ['applied_date', 'created_at', 'company_name', 'status']
    ordering = ['-applied_date', '-created_at']

    def get_queryset(self):
        """
        Always scope queries to the authenticated user.
        Users can never see or touch another user's applications.
        """
        return JobApplication.objects.filter(
            user=self.request.user
        ).select_related('user')

    def perform_create(self, serializer):
        """user is set inside the serializer's create() via request context."""
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Override destroy to return a meaningful message."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Application deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ─── Dashboard — Overall Stats ────────────────────────────────────────────────

class DashboardStatsView(APIView):
    """
    GET /api/dashboard/stats/

    Returns high-level counts for the authenticated user:

    Response 200:
    {
        "total": 42,
        "rejected": 10,
        "interviews": 8,
        "offers": 3,
        "joined": 1,
        "assessments": 5,
        "applied": 15
    }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = JobApplication.objects.filter(user=request.user)

        stats = {
            "total":       qs.count(),
            "applied":     qs.filter(status=ApplicationStatus.APPLIED).count(),
            "assessments": qs.filter(status=ApplicationStatus.ASSESSMENT).count(),
            "interviews":  qs.filter(status=ApplicationStatus.INTERVIEW_SCHEDULED).count(),
            "hr_round":    qs.filter(status=ApplicationStatus.HR_ROUND).count(),
            "rejected":    qs.filter(status=ApplicationStatus.REJECTED).count(),
            "offers":      qs.filter(status=ApplicationStatus.OFFER_RECEIVED).count(),
            "joined":      qs.filter(status=ApplicationStatus.JOINED).count(),
        }
        return Response(stats, status=status.HTTP_200_OK)


# ─── Dashboard — Monthly Trend ────────────────────────────────────────────────

class DashboardMonthlyView(APIView):
    """
    GET /api/dashboard/monthly/

    Returns application counts grouped by month for the last 12 months.

    Response 200:
    {
        "monthly_stats": [
            {"month": "2024-01", "count": 5},
            {"month": "2024-02", "count": 8},
            ...
        ]
    }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        twelve_months_ago = timezone.localdate() - timedelta(days=365)

        monthly_data = (
            JobApplication.objects
            .filter(user=request.user, applied_date__gte=twelve_months_ago)
            .annotate(month=TruncMonth('applied_date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        result = [
            {
                "month": entry['month'].strftime('%Y-%m'),
                "count": entry['count'],
            }
            for entry in monthly_data
        ]

        return Response({"monthly_stats": result}, status=status.HTTP_200_OK)


# ─── Dashboard — Platform Distribution ────────────────────────────────────────

class DashboardPlatformView(APIView):
    """
    GET /api/dashboard/platform/

    Returns application count per platform for the authenticated user.

    Response 200:
    {
        "platform_stats": [
            {"platform": "LinkedIn", "count": 18},
            {"platform": "Naukri", "count": 10},
            ...
        ]
    }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        platform_data = (
            JobApplication.objects
            .filter(user=request.user)
            .values('applied_platform')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        result = [
            {
                "platform": entry['applied_platform'],
                "count": entry['count'],
            }
            for entry in platform_data
        ]

        return Response({"platform_stats": result}, status=status.HTTP_200_OK)


# ─── Dashboard — Status Distribution ─────────────────────────────────────────

class DashboardStatusView(APIView):
    """
    GET /api/dashboard/status/

    Returns application count per status for the authenticated user.

    Response 200:
    {
        "status_stats": [
            {"status": "Applied", "count": 15},
            {"status": "Rejected", "count": 10},
            ...
        ]
    }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_data = (
            JobApplication.objects
            .filter(user=request.user)
            .values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        result = [
            {
                "status": entry['status'],
                "count": entry['count'],
            }
            for entry in status_data
        ]

        return Response({"status_stats": result}, status=status.HTTP_200_OK)
