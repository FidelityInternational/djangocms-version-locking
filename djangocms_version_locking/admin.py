from djangocms_versioning.admin import VersioningAdminMixin
from djangocms_versioning.models import Version


class VersionLockAdminMixin(VersioningAdminMixin):
    """
    Mixin providing versioning functionality to admin classes of
    version models.
    """

    def has_change_permission(self, request, content_obj=None):
        """
        If there’s a lock for edited object and if that lock belongs
        to the current user
        """
        version = Version.objects.get_for_content(content_obj)
        if (
            hasattr(version, 'versionlock') and
            request.user != version.versionlock.created_by
        ):
            return False
        return True
