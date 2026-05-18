"""
applications/admin.py
────────────────────────────────────────────────────────────────────
Registers JobApplication in the Django admin with useful list/filter views.
"""

from django.contrib import admin
from .models import JobApplication


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'company_name',
        'job_role',
        'applied_platform',
        'status',
        'applied_date',
        'created_at',
    ]
    list_filter = ['status', 'applied_platform', 'applied_date']
    search_fields = ['company_name', 'job_role', 'user__username', 'user__email']
    ordering = ['-applied_date']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Job Details', {
            'fields': ('company_name', 'job_role', 'job_description', 'job_url')
        }),
        ('Application Info', {
            'fields': ('user', 'applied_platform', 'applied_date', 'status', 'resume')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
