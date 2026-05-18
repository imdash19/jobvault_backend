# accounts/models.py
# ─────────────────────────────────────────────────────────────────────────────
# JobVault uses Django's built-in User model (django.contrib.auth.models.User)
# No custom model is required. All authentication is handled by SimpleJWT.
#
# Fields available on the default User:
#   id, username, email, first_name, last_name,
#   password (hashed), is_active, date_joined, last_login
#
# If you later need extra profile fields (phone, avatar, bio, etc.),
# add a UserProfile model here with a OneToOneField to User.
# ─────────────────────────────────────────────────────────────────────────────
