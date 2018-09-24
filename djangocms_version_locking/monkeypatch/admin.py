import types

from django.utils.translation import ugettext_lazy as _

from djangocms_versioning import admin, models, constants

from ..models import VersionLock


def new_save(old_save):
    """
    Override the save method to add a version lock
    """
    def inner(version, **kwargs):
        old_save(version, **kwargs)
        # A draft version is locked by default
        if version.state == constants.DRAFT:
            # create lock
            VersionLock.objects.create(
                version=version,
                created_by=version.created_by
            )
        # A any other state than draft has no lock, an existing lock should be removed
        else:
            VersionLock.objects.filter(version=version).delete()
        return version
    return inner
models.Version.save = new_save(models.Version.save)


# VersionAdmin new locked field
# FIXME: This will be an icon and will need to check for the existence of an icon.
def locked(self, version):
    if hasattr(version, "versionlock"):
        return "Yes"
    return ""
locked.short_description = _('locked')
admin.VersionAdmin.locked = locked


# Add the new defined locked field
def get_list_display(func):
    def inner(self, request):
        list_display = func(self, request)
        created_by_index = list_display.index('created_by')
        return list_display[:created_by_index] + ('locked', ) + list_display[created_by_index:]
    return inner
admin.VersionAdmin.get_list_display = get_list_display(admin.VersionAdmin.get_list_display)



#############################
# Unlock view
#############################

## Urls
from django.conf.urls import url

from cms.utils.urlutils import admin_reverse
from django.http import Http404, HttpResponseNotAllowed
from django.contrib import messages
from django.shortcuts import redirect

from django.contrib.admin.utils import unquote


def _unlock_view(self, request, object_id):
    """

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
    # Unlock the version
    #version.unlock(request.user)
    # Display message
    messages.success(request, _("Version unlocked"))

    # Redirect
    url = admin_reverse('{app}_{model}_changelist'.format(
        app=self.model._meta.app_label,
        model=self.model._meta.model_name,
    )) + '?grouper=' + str(version.grouper.pk)

    return redirect(url)
admin.VersionAdmin._unlock_view = _unlock_view


def _get_urls(func):
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


#########################
# Unlock Actions
########################
from django.template.loader import render_to_string

from django.urls import reverse

from ..helpers import content_is_unlocked

old_get_state_actions = admin.VersionAdmin.get_state_actions


def _get_unlock_link(self, obj, request, **kwargs):

    if not obj.state == constants.DRAFT and not hasattr(obj, "versionlock"):
        return ""

    # May
    if not content_is_unlocked(obj, request.user):
        return ""

    unlock_url = reverse('admin:{app}_{model}_unlock'.format(
        app=obj._meta.app_label, model=self.model._meta.model_name,
    ), args=(obj.pk,))

    return render_to_string(
        'djangocms_version_locking/admin/unlock_icon.html',
        {'unlock_url': unlock_url}
    )
admin.VersionAdmin._get_unlock_link = _get_unlock_link


def get_state_actions(func):
    def inner(self, *args, **kwargs):
        state_list = func(self, *args, **kwargs)
        state_list.append(self._get_unlock_link)
        return state_list
    return inner
admin.VersionAdmin.get_state_actions = get_state_actions(admin.VersionAdmin.get_state_actions)
