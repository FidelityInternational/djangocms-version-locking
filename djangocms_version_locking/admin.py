from djangocms_versioning.admin import VersioningAdminMixin


class VersionLockAdminMixin(VersioningAdminMixin):
    """
    Mixin providing versioning functionality to admin classes of
    version models.
    """

    def has_change_permission(self, request, obj=None):
        """
        If there’s a lock for edited object and if that lock belongs
        to the current user
        """
        from .helpers import content_is_unlocked

        # User has permissions?
        has_permission = super().has_change_permission(request, obj)
        if not has_permission:
            return False

        # Check if the lock exists and belongs to the user
        if obj:
            return content_is_unlocked(obj, request.user)
        return True
