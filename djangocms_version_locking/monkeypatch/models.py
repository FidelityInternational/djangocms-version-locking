from django.utils.translation import ugettext_lazy as _

from djangocms_versioning import models, constants
from djangocms_versioning.exceptions import ConditionFailed

from djangocms_version_locking.helpers import (
    create_version_lock,
    get_latest_draft_version,
    remove_version_lock,
    version_is_locked,
)


def new_save(old_save):
    """
    Override the Versioning save method to add a version lock
    """
    def inner(version, **kwargs):
        old_save(version, **kwargs)
        # A draft version is locked by default
        if version.state == constants.DRAFT:
            if not version_is_locked(version):
                # create a lock
                create_version_lock(version, version.created_by)
        # A any other state than draft has no lock, an existing lock should be removed
        else:
            remove_version_lock(version)
        return version
    return inner
models.Version.save = new_save(models.Version.save)


def _is_version_locked(message):
    def inner(version, user):
        lock = version_is_locked(version)
        if lock and lock.created_by != user:
            raise ConditionFailed(message.format(user=lock.created_by))
    return inner


def _is_draft_version_locked(message):
    def inner(version, user):
        try:
            # if there's a prepoluated field on version object
            # representing a draft lock, use it
            cached_draft_version_user_id = getattr(version, "_draft_version_user_id")
            if cached_draft_version_user_id and cached_draft_version_user_id != user.pk:
                raise ConditionFailed(
                    message.format(user="User #{}".format(cached_draft_version_user_id))
                )
        except AttributeError:
            draft_version = get_latest_draft_version(version)
            lock = version_is_locked(draft_version)
            if lock and lock.created_by != user:
                raise ConditionFailed(message.format(user=lock.created_by))
    return inner


error_message = _('Action Denied. The latest version is locked with {user}')
draft_error_message = _('Action Denied. The draft version is locked with {user}')


models.Version.check_archive += [_is_version_locked(error_message)]
models.Version.check_discard += [_is_version_locked(error_message)]
models.Version.check_revert += [_is_draft_version_locked(draft_error_message)]
models.Version.check_unpublish += [_is_draft_version_locked(draft_error_message)]
models.Version.check_edit_redirect += [_is_draft_version_locked(draft_error_message)]
