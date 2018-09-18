from djangocms_versioning.admin import VersioningAdminMixin

from djangocms_versioning.models import Version

class VersionLockAdminMixin(VersioningAdminMixin):
    """
    Mixin providing versioning functionality to admin classes of
    version models.
    """

    def has_change_permission(self, request, obj=None):
        """
        If there’s a lock for edited object and if that lock belongs to current user
        """
        if obj is None:
            return False

        # FIXME: A different user to the author could have unlock permissions!!!!
        version = Version.objects.get(pk=obj.pk)
        if (hasattr(version, 'versionlock') and
            (request.user != version.versionlock.created_by)):
                return False

        return True


