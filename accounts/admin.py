from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Re-register with default UserAdmin (already registered by Django,
# but shown here for completeness — no custom model needed)
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
