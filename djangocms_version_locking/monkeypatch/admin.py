from django.utils.translation import ugettext_lazy as _

from djangocms_versioning import admin, models


# VersionAdmin new locked field
def locked(self, obj):
    return obj.id
locked.short_description = _('locked')

# Replace the Version model admin class with a Versionlock class!
admin.VersionAdmin.locked = locked
# Add the new defined locked field
created_by_index = admin.VersionAdmin.list_display.index('created_by')
admin.VersionAdmin.list_display = admin.VersionAdmin.list_display[:created_by_index] + ('locked', ) + admin.VersionAdmin.list_display[created_by_index:]

