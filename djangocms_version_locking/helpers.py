from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_text

from .admin import VersionLockAdminMixin
from .models import VersionLock

try:
    from djangocms_internalsearch.helpers import emit_content_change
except ImportError:
    emit_content_change = None


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
    created = VersionLock.objects.create(
        version=version,
        created_by=user
    )
    if emit_content_change:
        emit_content_change(version.content)
    return created

def remove_version_lock(version):
    """
    Delete a version lock, handles when there are none available.
    """
    deleted = VersionLock.objects.filter(version=version).delete()
    if emit_content_change:
        emit_content_change(version.content)
    return deleted


def version_is_locked(version):
    """
    Determine if a version is locked
    """
    return getattr(version, "versionlock", None)


def version_is_unlocked_for_user(version, user):
    """Check if lock doesn't exist for a version object or is locked to provided user.
    """
    lock = version_is_locked(version)
    return lock is None or lock.created_by == user


def send_email(
    recipients,
    subject,
    template,
    template_context
):
    """
    Send emails using locking templates
    """
    template = 'djangocms_version_locking/emails/{}'.format(template)
    subject = force_text(subject)
    content = render_to_string(template, template_context)

    message = EmailMessage(
        subject=subject,
        body=content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )
    return message.send()


def get_latest_draft_version(version):
    """Get latest draft version of version object
    """
    from djangocms_versioning.models import Version
    from djangocms_versioning.constants import DRAFT

    drafts = (
        Version.objects
        .filter_by_content_grouping_values(version.content)
        .filter(state=DRAFT)
    )

    return drafts.first()
