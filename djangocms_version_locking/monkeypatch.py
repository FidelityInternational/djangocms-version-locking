from djangocms_versioning import admin, models

from .admin import VersionLockingAdmin


"""
# TODO: Create copy and save method overrides on the Version model!!
# Override the copy method to add a version lock
def copy(*args, **kwargs):
    version = models.Version.copy(*args, **kwargs)
    #TODO: <create lock here>
    return version
models.Version.copy = copy
"""

# Replace the versioning admin instance with a locking version!
admin.VersionAdmin.locked = VersionLockingAdmin.locked
admin.VersionAdmin.list_display = VersionLockingAdmin.list_display
