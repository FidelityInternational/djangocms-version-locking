from django.utils.translation import gettext_lazy as _

from djangocms_moderation import models as moderation_model
from djangocms_moderation.helpers import (
    get_moderated_children_from_placeholder,
)
from djangocms_versioning import constants, models
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


def _add_nested_children(self, version, parent_node):
    """
    Helper method which finds moderated children and adds them to the collection if
    it's not locked by a user
    """
    parent = version.content
    added_items = 0
    if not getattr(parent, "get_placeholders", None):
        return added_items

    for placeholder in parent.get_placeholders():
        for child_version in get_moderated_children_from_placeholder(
                placeholder, version.versionable.grouping_values(parent)
        ):
            # Don't add the version if it's locked by another user
            child_version_locked = version_is_locked(child_version)
            if not child_version_locked:
                moderation_request, _added_items = self.add_version(
                    child_version, parent=parent_node, include_children=True
                )
            else:
                _added_items = self._add_nested_children(child_version, parent_node)
            added_items += _added_items
    return added_items


moderation_model.ModerationCollection._add_nested_children = _add_nested_children
