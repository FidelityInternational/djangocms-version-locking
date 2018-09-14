from django.contrib import admin

from djangocms_versioning.admin import VersioningAdminMixin

from .models import VersionLock


class VersionLockAdminMixin(VersioningAdminMixin):
    """
    Mixin providing versioning functionality to admin classes of
    version models.
    """

    """
    TODO: Implement permissions
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    """
