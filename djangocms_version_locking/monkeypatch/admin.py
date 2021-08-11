from django.conf.urls import url
from django.contrib import messages
from django.contrib.admin.utils import unquote
from django.http import Http404, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from djangocms_versioning import admin, constants
from djangocms_versioning.constants import DRAFT
from djangocms_versioning.helpers import version_list_url

from djangocms_version_locking.emails import (
    notify_version_author_version_unlocked,
)
from djangocms_version_locking.helpers import (
    remove_version_lock,
    version_is_locked,
)


def locked(self, version):
    """
    Generate a locked field for Versioning Admin
    """
    if version.state == constants.DRAFT and version_is_locked(version):
        return render_to_string('djangocms_version_locking/admin/locked_icon.html')
    return ""


locked.short_description = _('locked')
admin.VersionAdmin.locked = locked


def is_locked(self, obj):
    version = self.get_version(obj)
    if version.state == DRAFT and version_is_locked(version):
        return render_to_string("djangocms_version_locking/admin/locked_icon.html", {"disabled": True})
    return ""


is_locked.short_description = _('locked')
admin.ExtendedVersionAdminMixin.locked = is_locked


def get_list_display(func):
    """
    Register the locked field with the Versioning Admin
    """
    def inner(self, request):
        list_display = func(self, request)
        created_by_index = list_display.index('created_by')
        return list_display[:created_by_index] + ('locked', ) + list_display[created_by_index:]
    return inner


admin.VersionAdmin.get_list_display = get_list_display(admin.VersionAdmin.get_list_display)


def get_extended_list_display(func):
    """
    Register the locked field with the ExtendedVersionAdminMixin
    """
    def inner(self, request):
        list_display = func(self, request)
        versioning_state_index = list_display.index('get_versioning_state')
        return tuple(list_display[:versioning_state_index] + 'locked' + list_display[versioning_state_index:])
    return inner


admin.ExtendedVersionAdminMixin.list_display = get_extended_list_display(
    admin.ExtendedVersionAdminMixin.list_display
)


def _unlock_view(self, request, object_id):
    """
    Unlock a locked version
    """
    # This view always changes data so only POST requests should work
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], _('This view only supports POST method.'))

    # Check version exists
    version = self.get_object(request, unquote(object_id))
    if version is None:
        return self._get_obj_does_not_exist_redirect(
            request, self.model._meta, object_id)

    # Raise 404 if not locked
    if version.state != constants.DRAFT:
        raise Http404

    # Check that the user has unlock permission
    if not request.user.has_perm('djangocms_version_locking.delete_versionlock'):
        return HttpResponseForbidden(force_text(_("You do not have permission to remove the version lock")))

    # Unlock the version
    remove_version_lock(version)
    # Display message
    messages.success(request, _("Version unlocked"))

    # Send an email notification
    notify_version_author_version_unlocked(version, request.user)

    # Redirect
    url = version_list_url(version.content)
    return redirect(url)


admin.VersionAdmin._unlock_view = _unlock_view


def _get_unlock_link(self, obj, request):
    """
    Generate an unlock link for the Versioning Admin
    """
    # If the version is not draft no action should be present
    if obj.state != constants.DRAFT or not version_is_locked(obj):
        return ""

    disabled = True
    # Check whether the lock can be removed
    # Check that the user has unlock permission
    if version_is_locked(obj) and request.user.has_perm('djangocms_version_locking.delete_versionlock'):
        disabled = False

    unlock_url = reverse('admin:{app}_{model}_unlock'.format(
        app=obj._meta.app_label, model=self.model._meta.model_name,
    ), args=(obj.pk,))

    return render_to_string(
        'djangocms_version_locking/admin/unlock_icon.html',
        {
            'unlock_url': unlock_url,
            'disabled': disabled
        }
    )


admin.VersionAdmin._get_unlock_link = _get_unlock_link


def _get_urls(func):
    """
    Add custom Version Lock urls to Versioning urls
    """
    def inner(self, *args, **kwargs):
        url_list = func(self, *args, **kwargs)
        info = self.model._meta.app_label, self.model._meta.model_name
        url_list.insert(0, url(
            r'^(.+)/unlock/$',
            self.admin_site.admin_view(self._unlock_view),
            name='{}_{}_unlock'.format(*info),
        ))
        return url_list
    return inner


admin.VersionAdmin.get_urls = _get_urls(admin.VersionAdmin.get_urls)


def get_state_actions(func):
    """
    Add custom Version Lock actions to Versioning state actions
    """
    def inner(self, *args, **kwargs):
        state_list = func(self, *args, **kwargs)
        state_list.append(self._get_unlock_link)
        return state_list
    return inner


admin.VersionAdmin.get_state_actions = get_state_actions(admin.VersionAdmin.get_state_actions)


def _get_edit_redirect_version(func):
    """
    Override the Versioning Admin edit redirect to add a user as a version author if no lock exists
    """
    def inner(self, request, object_id):
        version = func(self, request, object_id)
        if version is not None:
            # Add the current user as the version author
            # Saving the version will Add a lock to the current user editing now it's in an unlocked state
            version.created_by = request.user
            version.save()
        return version
    return inner


admin.VersionAdmin._get_edit_redirect_version = _get_edit_redirect_version(
    admin.VersionAdmin._get_edit_redirect_version
)


# Add Version Locking css media to the Versioning Admin instance
additional_css = ('djangocms_version_locking/css/version-locking.css',)
admin.VersionAdmin.Media.css['all'] = admin.VersionAdmin.Media.css['all'] + additional_css
admin.ExtendedVersionAdminMixin.Media.css['all'] = admin.ExtendedVersionAdminMixin.Media.css['all'] + additional_css
