from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html

from cms.toolbar.items import ButtonList

from djangocms_versioning.cms_toolbars import VersioningToolbar

from djangocms_version_locking.helpers import content_is_unlocked_for_user


def new_edit_button(func):
    def inner(self, **kwargs):
        # Only run this if model is versioned and in content mode.
        if not self._is_versioned() or not self.toolbar.content_mode_active:
            return

        # Check whether current toolbar object has a version lock.
        if content_is_unlocked_for_user(self.toolbar.obj, self.request.user):
            # No version lock. Call original func to render edit button.
            func(self, **kwargs)
            return

        # There is a version lock for the current object.
        # Add a disabled edit button.
        item = ButtonList(side=self.toolbar.RIGHT)
        item.add_button(
            format_html(
                '<span style="vertical-align:middle;position:relative;top:-1px" class="cms-icon cms-icon-lock"></span>{name}',
                name=_('Edit'),
            ),
            url='javascript:void(0)',
            disabled=True,
            extra_classes=['cms-btn-action', 'cms-version-locking-btn-icon'],
        )
        self.toolbar.add_item(item)
    return inner
VersioningToolbar._add_edit_button = new_edit_button(VersioningToolbar._add_edit_button)
