"""
applications/serializers.py
────────────────────────────────────────────────────────────────────
Serializers:
  • JobApplicationSerializer — full CRUD for a job application
    - Validates applied_date (no future dates)
    - Validates resume file extension (pdf, doc, docx) and size
    - Auto-sets applied_date to today if not provided
    - user field is read-only (set from request.user in view)
"""

import os
from django.utils import timezone
from django.conf import settings
from rest_framework import serializers

from .models import JobApplication, ApplicationStatus, AppliedPlatform


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Full serializer for JobApplication.

    Read-only fields  : user, created_at, updated_at
    Auto-filled fields: applied_date (defaults to today)
    Validated fields  : applied_date (no future), resume (extension + size)
    """

    # Show username alongside user id in responses
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)

    # Human-readable labels for choice fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    platform_display = serializers.CharField(
        source='get_applied_platform_display', read_only=True
    )

    class Meta:
        model = JobApplication
        fields = [
            'id',
            'user',
            'username',
            'company_name',
            'job_role',
            'job_description',
            'applied_platform',
            'platform_display',
            'job_url',
            'resume',
            'applied_date',
            'status',
            'status_display',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'username', 'created_at', 'updated_at',
                            'status_display', 'platform_display']

    # ── Helpers ───────────────────────────────────────────────────────────────

    def get_username(self, obj):
        return obj.user.username

    # ── Field Validations ─────────────────────────────────────────────────────

    def validate_applied_date(self, value):
        """Reject applied dates set in the future."""
        if value > timezone.localdate():
            raise serializers.ValidationError(
                "Applied date cannot be in the future."
            )
        return value

    def validate_resume(self, value):
        """
        Validate:
          1. File extension must be .pdf, .doc, or .docx
          2. File size must not exceed MAX_RESUME_SIZE_MB
        """
        if value is None:
            return value

        allowed_extensions = getattr(
            settings, 'ALLOWED_RESUME_EXTENSIONS', ['.pdf', '.doc', '.docx']
        )
        max_size_mb = getattr(settings, 'MAX_RESUME_SIZE_MB', 5)

        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Invalid file type '{ext}'. Allowed types: "
                f"{', '.join(allowed_extensions)}."
            )

        max_size_bytes = max_size_mb * 1024 * 1024
        if value.size > max_size_bytes:
            raise serializers.ValidationError(
                f"File size must not exceed {max_size_mb} MB. "
                f"Your file is {value.size / (1024 * 1024):.1f} MB."
            )

        return value

    # ── Object-Level Validation ───────────────────────────────────────────────

    def validate(self, attrs):
        """
        If applied_date is not provided at all (create), default to today.
        This runs after field-level validators.
        """
        if 'applied_date' not in attrs or attrs.get('applied_date') is None:
            attrs['applied_date'] = timezone.localdate()
        return attrs

    # ── Create / Update ───────────────────────────────────────────────────────

    def create(self, validated_data):
        """Inject request.user as the application owner."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
