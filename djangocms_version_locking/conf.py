from django.conf import settings


EMAIL_NOTIFICATIONS_FAIL_SILENTLY = getattr(
    settings, "EMAIL_NOTIFICATIONS_FAIL_SILENTLY", False
)
