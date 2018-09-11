from django.contrib import admin

from .models import VersionLock


class VersionLockAdminMixin:
    """
    Mixin providing versioning functionality to admin classes of
    version models.
    """
    def save_model(self, request, obj, form, change):
        """
        Overrides the save method to create a version object
        when a content object is created
        """
        super().save_model(request, version_obj, form, change)
        if not change:
            # create a new version lock object and save it
            VersionLock.objects.create(version=version_obj, created_by=request.user)


class VersionLockingAdmin(admin.ModelAdmin):
    """
    Admin class used for version locked models.
    """
    list_display = (
        'created',
        'created_by',
        'version',
    )
    list_display_links = None

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
