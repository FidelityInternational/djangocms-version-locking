from djangocms_versioning import admin

from .admin import VersionLockingAdmin

# Replace the verisoning admin instance with a locking version!
admin.VersionAdmin = VersionLockingAdmin
