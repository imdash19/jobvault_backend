"""
applications/models.py
────────────────────────────────────────────────────────────────────
JobApplication model — tracks every job application for a user.

Choices:
  STATUS_CHOICES    — 7 application statuses
  PLATFORM_CHOICES  — 9 job platforms

Validation:
  - applied_date cannot be in the future (enforced in clean() and serializer)
  - applied_date defaults to today if not provided
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


# ─── Choice Constants ─────────────────────────────────────────────────────────

class ApplicationStatus(models.TextChoices):
    APPLIED              = 'Applied',              'Applied'
    ASSESSMENT           = 'Assessment',           'Assessment'
    INTERVIEW_SCHEDULED  = 'Interview Scheduled',  'Interview Scheduled'
    HR_ROUND             = 'HR Round',             'HR Round'
    REJECTED             = 'Rejected',             'Rejected'
    OFFER_RECEIVED       = 'Offer Received',       'Offer Received'
    JOINED               = 'Joined',               'Joined'


class AppliedPlatform(models.TextChoices):
    LINKEDIN         = 'LinkedIn',         'LinkedIn'
    NAUKRI           = 'Naukri',           'Naukri'
    INDEED           = 'Indeed',           'Indeed'
    WELLFOUND        = 'Wellfound',        'Wellfound'
    INTERNSHALA      = 'Internshala',      'Internshala'
    FOUNDIT          = 'Foundit',          'Foundit'
    COMPANY_WEBSITE  = 'Company Website',  'Company Website'
    REFERRAL         = 'Referral',         'Referral'
    OTHER            = 'Other',            'Other'


# ─── Model ────────────────────────────────────────────────────────────────────

class JobApplication(models.Model):
    """
    Represents a single job application made by a user.

    Relationships:
        user → auth.User  (each application belongs to one user)

    Key behaviours:
        • applied_date auto-fills to today if omitted
        • applied_date in the future raises ValidationError
        • resume upload limited to PDF/DOC/DOCX (validated in serializer)
    """

    # Owner
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job_applications',
    )

    # Job Details
    company_name = models.CharField(max_length=200)
    job_role = models.CharField(max_length=200)
    job_description = models.TextField(blank=True, default='')
    applied_platform = models.CharField(
        max_length=50,
        choices=AppliedPlatform.choices,
        default=AppliedPlatform.OTHER,
    )
    job_url = models.URLField(max_length=500, blank=True, default='')

    # Resume
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
    )

    # Dates & Status
    applied_date = models.DateField(default=timezone.localdate)
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.APPLIED,
    )

    # Notes
    notes = models.TextField(blank=True, default='')

    # Timestamps (auto-managed)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ── Validation ────────────────────────────────────────────────────────────

    def clean(self):
        """Reject applied_date set to a future date."""
        if self.applied_date and self.applied_date > timezone.localdate():
            raise ValidationError(
                {"applied_date": "Applied date cannot be in the future."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # ── Meta ──────────────────────────────────────────────────────────────────

    class Meta:
        ordering = ['-applied_date', '-created_at']
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'applied_platform']),
            models.Index(fields=['user', 'applied_date']),
        ]

    def __str__(self):
        return f"{self.job_role} @ {self.company_name} ({self.user.username})"
