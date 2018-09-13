from django.conf import settings

from cms.app_base import CMSAppConfig, CMSAppExtension
from cms.models import PageContent

from .helpers import replace_admin_for_models


class VersionLockingCMSExtension(CMSAppExtension):

    def __init__(self):
        from . import monkeypatch

    def handle_admin_classes(self, cms_config):
        """
        Replaces admin model classes for all registered content types
        with an admin model class that inherits from VersioningAdminMixin.
        """
        replace_admin_for_models(
            [lockable['locking_model'] for lockable in cms_config.version_lock_list],
        )

    def configure_app(self, cms_config):
        self.handle_admin_classes(cms_config)


class VersionLockingCMSConfig(CMSAppConfig):
    """
    Register the app with Django CMS
    """
    djangocms_version_locking_enabled = getattr(
        settings, 'VERSION_LOCKING_CMS_MODELS_ENABLED', True)
    version_lock_list = [
        {
            'locking_model': PageContent,
        }
    ]

