from django.template.loader import render_to_string
from django.utils.html import format_html

from cms.app_base import CMSAppConfig, CMSAppExtension

from djangocms_alias.models import AliasContent
from djangocms_versioning.constants import DRAFT

from djangocms_version_locking.helpers import version_is_locked


def add_alias_version_lock(obj, field):
    version = obj.versions.all()[0]
    if version.state == DRAFT and version_is_locked(version):
        lock_icon = render_to_string("djangocms_version_locking/admin/locked_mixin_icon.html")
    else:
        lock_icon = ""
    return format_html(
        "{is_locked}{field_value}",
        is_locked=lock_icon,
        field_value=getattr(obj, field),
    )


class VersionLockingCMSExtension(CMSAppExtension):
    def __init__(self):
        # The monkey patch is here to be sure that at module load time the Version class
        # is registered and can be overriden without requiring a strict load order
        # in the INSTALLED_APPS setting in a projects settings.py. This is why this patch
        # Isn't loaded from: VersionLockingConfig.ready
        from .monkeypatch import admin as monkeypatch_admin  # noqa: F401

    def configure_app(self, cms_config):
        pass


class VersionLockingCMSAppConfig(CMSAppConfig):
    djangocms_versioning_enabled = True
    versioning = []
    extended_admin_field_modifiers = [{AliasContent: {"name": add_alias_version_lock}}, ]
