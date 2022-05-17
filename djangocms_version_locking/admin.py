from django.template.loader import render_to_string

from djangocms_versioning.admin import VersioningAdminMixin
from djangocms_versioning.constants import DRAFT


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
        from .helpers import content_is_unlocked_for_user

        # User has permissions?
        has_permission = super().has_change_permission(request, obj)
        if not has_permission:
            return False

        # Check if the lock exists and belongs to the user
        if obj:
            return content_is_unlocked_for_user(obj, request.user)
        return True

class VersionLockContentAdminMixin(VersioningAdminMixin):
    def get_list_display(self, request):
        list_display = self.list_display
        return ("get_locked_name", ) + list_display[1:]

    def get_locked_name(self, obj):
        from djangocms_version_locking.helpers import version_is_locked
        version = obj.versions.all()[0]
        if version.state == DRAFT and version_is_locked(version):
            lock_icon = render_to_string("djangocms_version_locking/admin/locked_icon.html")
            return f"{lock_icon}{obj.__str__()}"
