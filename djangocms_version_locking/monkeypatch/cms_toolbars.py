from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html

from cms.toolbar.items import Button, ButtonList

from djangocms_versioning.cms_toolbars import VersioningToolbar

from djangocms_version_locking.helpers import content_is_unlocked_for_user, get_lock_for_content


class ButtonWithAttributes(Button):
    template = "djangocms_version_locking/toolbar/items/button_with_attributes.html"

    def __init__(self, name, url, active=False, disabled=False,
                 extra_classes=None, html_attributes=None):
        super().__init__(name, url, active, disabled, extra_classes)

        self.html_attributes = html_attributes

    def get_context(self):
        context = super().get_context()
        context['html_attributes'] = self.html_attributes
        return context


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

        # Populate a title with the locked author details
        html_attributes = {}
        version_lock = get_lock_for_content(self.toolbar.obj)
        if version_lock:
            # If the users name is available use it, otherwise use their username
            html_attributes['title'] = _("Locked with {name}").format(
                name=version_lock.created_by.get_full_name() or version_lock.created_by.username,
            )

        # There is a version lock for the current object.
        # Add a disabled edit button.
        item_list = ButtonList(side=self.toolbar.RIGHT)
        button = ButtonWithAttributes(
            format_html(
                '<span style="vertical-align:middle;position:relative;top:-1px" '
                'class="cms-icon cms-icon-lock"></span>{name}',
                name=_('Edit'),
            ),
            url='javascript:void(0)',
            disabled=True,
            extra_classes=['cms-btn-action', 'cms-version-locking-btn-icon'],
            html_attributes=html_attributes,
        )
        item_list.buttons.append(button)
        self.toolbar.add_item(item_list)
    return inner


VersioningToolbar._add_edit_button = new_edit_button(VersioningToolbar._add_edit_button)
