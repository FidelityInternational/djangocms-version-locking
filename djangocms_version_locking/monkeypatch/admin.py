from django.conf.urls import url
from django.contrib import messages
from django.contrib.admin.utils import unquote
from django.http import Http404, HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from cms.utils.urlutils import admin_reverse

from djangocms_versioning import admin, models, constants

from djangocms_version_locking.helpers import (
    create_version_lock,
    is_draft_locked,
    is_draft_unlocked,
    remove_version_lock
)


def new_save(old_save):
    """
    Override the Versioning save method to add a version lock
    """
    def inner(version, **kwargs):
        old_save(version, **kwargs)
        # A draft version is locked by default
        if is_draft_unlocked(version):
            # create a lock
            create_version_lock(version, version.created_by)
        # A any other state than draft has no lock, an existing lock should be removed
        else:
            remove_version_lock(version)
        return version
    return inner
models.Version.save = new_save(models.Version.save)


def locked(self, version):
    """
    Generate an locked field for Versioning Admin
    """
    if is_draft_locked(version):
        return render_to_string('djangocms_version_locking/admin/locked_icon.html')
    return ""
locked.short_description = _('locked')
admin.VersionAdmin.locked = locked


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

    # Redirect
    url = admin_reverse('{app}_{model}_changelist'.format(
        app=self.model._meta.app_label,
        model=self.model._meta.model_name,
    )) + '?grouper=' + str(version.grouper.pk)

    return redirect(url)
admin.VersionAdmin._unlock_view = _unlock_view


def _get_unlock_link(self, obj, request):
    """
    Generate an unlock link for the Versioning Admin
    """
    # If the version is not draft no action should be present
    if obj.state != constants.DRAFT:
        return ""

    # Check whether the lock can be removed
    # Check that the user has unlock permission
    if is_draft_locked(obj) and request.user.has_perm('djangocms_version_locking.delete_versionlock'):
        unlock_url = reverse('admin:{app}_{model}_unlock'.format(
            app=obj._meta.app_label, model=self.model._meta.model_name,
        ), args=(obj.pk,))

        return render_to_string(
            'djangocms_version_locking/admin/unlock_icon.html',
            {'unlock_url': unlock_url}
        )

    return render_to_string(
        'djangocms_version_locking/admin/unlock_disabled_icon.html',
    )
admin.VersionAdmin._get_unlock_link = _get_unlock_link


def _get_urls(func):
    """
    Add custom Version Lock urls to Versioning urls
    """
    def inner(self, *args, **kwargs):
        url_list = func(self, *args, **kwargs)
        info = self.model._meta.app_label, self.model._meta.model_name
        url_list.insert(0,
            url(
                r'^(.+)/unlock/$',
                self.admin_site.admin_view(self._unlock_view),
                name='{}_{}_unlock'.format(*info),
            )
        )
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


def edit_redirect_view(func):
    """
    Override the Versioning Admin edit redirect to add a user as a version author if no lock exists
    """
    def inner(self, request, object_id):

        # Duplicated checks to ensure thta we aren't changing anything that would be invalid
        # This view always changes data so only POST requests should work
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'], _('This view only supports POST method.'))

        version = self._get_edit_redirect_version(request, object_id)

        if version is None:
            raise Http404

        # If the version is a draft and has no lock
        if is_draft_unlocked(version):
            # Add the current user as the version author
            # Saving the version will Add a lock to the current user editing now it's in an unlocked state
            version.created_by = request.user
            version.save()

        return func(self, request, object_id)
    return inner
admin.VersionAdmin.edit_redirect_view = edit_redirect_view(admin.VersionAdmin.edit_redirect_view)
