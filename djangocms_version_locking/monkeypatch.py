from djangocms_versioning import admin

from .admin import VersionLockingAdmin



# Replace the versioning admin instance with a locking version!
admin.VersionAdmin.locked = VersionLockingAdmin.locked
admin.VersionAdmin.list_display = VersionLockingAdmin.list_display
