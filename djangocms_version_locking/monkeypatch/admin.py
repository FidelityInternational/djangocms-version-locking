from django.utils.translation import ugettext_lazy as _

from djangocms_versioning import admin, models, constants

from ..models import VersionLock


# FIXME: Move to a new patch file called models, second import in cms_config or app ready method?
# Override the save method to add a version lock
master_version_save = models.Version.save
def save(version, **kwargs):
    master_version_save(version, **kwargs)

    # A draft version is locked by default
    if version.state == constants.DRAFT:
        # create lock
        VersionLock.objects.create(
            version=version,
            created_by=version.created_by # TODO: Find out if this user is ok to use, could it be different. TEST!!
        )
    # A published version has no lock, an existing lock should be removed
    elif version.state == constants.PUBLISHED:
        # TODO: Catch a potential for the version to not exist
        VersionLock.objects.get(version=version).delete()
    return version
models.Version.save = save

# VersionAdmin new locked field
def locked(self, version):
    if version.versionlock:
        return "Yes"
    return ""
locked.short_description = _('locked')

# Replace the Version model admin class with a Versionlock class!
admin.VersionAdmin.locked = locked
# Add the new defined locked field
created_by_index = admin.VersionAdmin.list_display.index('created_by')
admin.VersionAdmin.list_display = admin.VersionAdmin.list_display[:created_by_index] + ('locked', ) + admin.VersionAdmin.list_display[created_by_index:]

