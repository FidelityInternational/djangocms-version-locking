from djangocms_versioning import admin, models, constants

from .admin import VersionLockingAdmin
from .models import VersionLock


master_version_save = models.Version.save
# Override the save method to add a version lock
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

# Replace the versioning admin instance with a locking version!
admin.VersionAdmin.locked = VersionLockingAdmin.locked
admin.VersionAdmin.list_display = VersionLockingAdmin.list_display
