"""
applications/filters.py
────────────────────────────────────────────────────────────────────
FilterSet for JobApplication:
  • Filter by: status, applied_platform, applied_date (exact/range)
  • Search  : company_name, job_role  (handled by SearchFilter in views)
"""

import django_filters
from .models import JobApplication, ApplicationStatus, AppliedPlatform


class ApplicationFilter(django_filters.FilterSet):
    """
    Allows filtering job applications via query parameters:

      ?status=Applied
      ?applied_platform=LinkedIn
      ?applied_date=2024-06-01
      ?applied_date_from=2024-01-01&applied_date_to=2024-06-30
    """

    # Exact match filters
    status = django_filters.ChoiceFilter(choices=ApplicationStatus.choices)
    applied_platform = django_filters.ChoiceFilter(choices=AppliedPlatform.choices)

    # Date exact match
    applied_date = django_filters.DateFilter(field_name='applied_date')

    # Date range filters
    applied_date_from = django_filters.DateFilter(
        field_name='applied_date',
        lookup_expr='gte',
        label='Applied date from (YYYY-MM-DD)',
    )
    applied_date_to = django_filters.DateFilter(
        field_name='applied_date',
        lookup_expr='lte',
        label='Applied date to (YYYY-MM-DD)',
    )

    class Meta:
        model = JobApplication
        fields = ['status', 'applied_platform', 'applied_date']
