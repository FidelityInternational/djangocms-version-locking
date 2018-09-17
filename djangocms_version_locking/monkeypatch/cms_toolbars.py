from django.utils.translation import ugettext_lazy as _

from cms.toolbar.items import ButtonList

from djangocms_versioning.cms_toolbars import VersioningToolbar

from djangocms_version_locking.helpers import content_is_unlocked


_original_add_edit_button = VersioningToolbar._add_edit_button


def _new_add_edit_button(self):
    # Only run this in content mode.
    if not self.toolbar.obj or not self.toolbar.content_mode_active:
        return

    # Check whether current toolbar object has a version lock.
    if content_is_unlocked(self.toolbar.obj, self.request.user):
        # No version lock. Call super function to render edit button.
        _original_add_edit_button(self)
        return

    # There is a version lock for the current object.
    # Add a disabled edit button.
    item = ButtonList(side=self.toolbar.RIGHT)
    item.add_button(
        _('Edit'),
        url='',
        disabled=True,
        extra_classes=['cms-btn-action', 'cms-icon', 'cms-icon-lock'],
    )
    self.toolbar.add_item(item)


VersioningToolbar._add_edit_button = _new_add_edit_button
