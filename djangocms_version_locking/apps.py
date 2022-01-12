from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VersionLockingConfig(AppConfig):
    name = "djangocms_version_locking"
    verbose_name = _("django CMS Version Locking")

    def ready(self):
        from .monkeypatch import checks, cms_toolbars, models  # noqa: F401
