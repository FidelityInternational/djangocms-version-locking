from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from djangocms_versioning import constants

from .admin import VersionLockAdminMixin
from .models import VersionLock


def version_lock_admin_factory(admin_class):
    """A class factory returning admin class with overriden
    versioning functionality.

    :param admin_class: Existing admin class
    :return: A subclass of `VersionLockAdminMixin` and `admin_class`
    """
    return type('VersionLocking' + admin_class.__name__, (VersionLockAdminMixin, admin_class), {})


def _replace_admin_for_model(modeladmin, admin_site):
    """Replaces existing admin class registered for `modeladmin.model` with
    a subclass that includes version locking functionality.

    Doesn't do anything if `modeladmin` is already an instance of
    `VersionLockAdminMixin`.

    :param model: ModelAdmin instance
    :param admin_site: AdminSite instance
    """
    if isinstance(modeladmin, VersionLockAdminMixin):
        return
    new_admin_class = version_lock_admin_factory(modeladmin.__class__)
    admin_site.unregister(modeladmin.model)
    admin_site.register(modeladmin.model, new_admin_class)


def replace_admin_for_models(models, admin_site=None):
    """
    :param models: List of model classes
    :param admin_site: AdminSite instance
    """
    if admin_site is None:
        admin_site = admin.site
    for model in models:
        try:
            modeladmin = admin_site._registry[model]
        except KeyError:
            continue
        _replace_admin_for_model(modeladmin, admin_site)


def content_is_unlocked_for_user(content, user):
    """Check if lock doesn't exist or object is locked to provided user.
    """
    try:
        lock = VersionLock.objects.get(
            version__content_type=ContentType.objects.get_for_model(content),
            version__object_id=content.pk,
        )
    except VersionLock.DoesNotExist:
        return True
    return lock.created_by == user


def placeholder_content_is_unlocked_for_user(placeholder, user):
    """Check if lock doesn't exist or placeholder source object
    is locked to provided user.
    """
    content = placeholder.source
    return content_is_unlocked_for_user(content, user)


def create_version_lock(version, user):
    """
    Create a version lock
    """
    return VersionLock.objects.create(
        version=version,
        created_by=user
    )


def remove_version_lock(version):
    """
    Delete a version lock, handles when there are none available.
    """
    return VersionLock.objects.filter(version=version).delete()


def version_is_locked(version):
    """
    Determine if a version is locked
    """
    return getattr(version, "versionlock", None)

def is_draft_unlocked(version):
    """
    Determine if the version is draft and unlocked
    """
    return version.state == constants.DRAFT and not version_is_locked(version)
