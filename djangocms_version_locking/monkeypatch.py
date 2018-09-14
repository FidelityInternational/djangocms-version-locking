from django.utils.translation import ugettext_lazy as _

from djangocms_versioning import admin, models


# VersionAdmin new locked field
def locked(self, obj):
    return obj.id
locked.short_description = _('version locked')

# Replace the Version model admin class with a Versionlock class!
admin.VersionAdmin.locked = locked
admin.VersionAdmin.list_display = (
    'nr',
    'created',
    'created_by',
    'locked',
    'state',
    'state_actions',
)
