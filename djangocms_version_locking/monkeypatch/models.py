from djangocms_versioning import models, constants

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


def _is_version_locked(version, user):
    lock = version_is_locked(version)
    return not lock or lock.created_by == user


def _is_draft_version_locked(version, user):
    draft_version = get_latest_draft_version(version)
    lock = version_is_locked(draft_version)
    return not lock or lock.created_by == user


models.Version.can_archive += [_is_version_locked]
models.Version.can_discard += [_is_version_locked]
models.Version.can_revert += [_is_draft_version_locked]
models.Version.can_unpublish += [_is_draft_version_locked]
