from django.utils.translation import ugettext_lazy as _

from djangocms_versioning import admin, models, constants

from ..models import VersionLock


def new_save(old_save):
    """
    Override the save method to add a version lock
    """
    def inner(version, **kwargs):
        old_save(version, **kwargs)
        # A draft version is locked by default
        if version.state == constants.DRAFT:
            # create lock
            VersionLock.objects.create(
                version=version,
                created_by=version.created_by
            )
        # A any other state than draft has no lock, an existing lock should be removed
        else:
            VersionLock.objects.filter(version=version).delete()
        return version
    return inner
models.Version.save = new_save(models.Version.save)


# VersionAdmin new locked field
# FIXME: This will be an icon and will need to check for the existence of an icon.
def locked(self, version):
    if hasattr(version, "versionlock"):
        return "Yes"
    return ""
locked.short_description = _('locked')
admin.VersionAdmin.locked = locked


# Add the new defined locked field
def get_list_display(func):
    def inner(self, request):
        list_display = func(self, request)
        created_by_index = list_display.index('created_by')
        return list_display[:created_by_index] + ('locked', ) + list_display[created_by_index:]
    return inner
admin.VersionAdmin.get_list_display = get_list_display(admin.VersionAdmin.get_list_display)
