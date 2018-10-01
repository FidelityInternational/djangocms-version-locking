import collections

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from cms.app_base import CMSAppConfig, CMSAppExtension
from cms.models import PageContent

from .helpers import replace_admin_for_models


class VersionLockingCMSExtension(CMSAppExtension):

    def __init__(self):
        # The monkey patch is here to be sure that at module load time the Version class
        # is registered and can be overriden without requiring a strict load order
        # in the INSTALLED_APPS setting in a projects settings.py. This is why this patch
        # Isn't loaded from: VersionLockingConfig.ready
        from .monkeypatch import admin as monkeypatch_admin

    def handle_admin_classes(self, cms_config):
        """
        Replaces admin model classes for all registered content types
        with an admin model class that inherits from VersioningAdminMixin.
        """
        replace_admin_for_models(cms_config.version_lock_models)

    def _lock_model_in_version_list(self, check_item, version_list):
        for version_model in version_list:
            if check_item == version_model.content_model:
                return True
        return False

    def handle_settings(self, cms_config):

        # Check that versioning is enabled
        versioning_enabled = getattr(cms_config, 'djangocms_versioning_enabled', False)
        if not versioning_enabled:
            raise ImproperlyConfigured('djangocms-versioning is not enabled.')

        # Check that the version_lock_models is a list
        if not isinstance(cms_config.version_lock_models, collections.abc.Iterable):
            raise ImproperlyConfigured("version_lock_models is not defined as an iterable")

        # FIXME: Currently there's no way to check whats been registered with versioning, the
        #       App config would need to allow a view of other apps configs
        # Check that the registered locking models are also registered with versioning
        # for lock_model in cms_config.version_lock_models:
        #     if not self._lock_model_in_version_list(lock_model, cms_config.versioning):
        #         raise ImproperlyConfigured("%s is not defined in djangocms_versioning" % lock_model)

    def configure_app(self, cms_config):
        self.handle_settings(cms_config)
        self.handle_admin_classes(cms_config)


class VersionLockingCMSConfig(CMSAppConfig):
    """
    Register the app with Django CMS
    """
    djangocms_version_locking_enabled = getattr(
        settings, 'VERSION_LOCKING_CMS_MODELS_ENABLED', True)
    version_lock_models = [PageContent, ]

    # Versioning dependant
    djangocms_versioning_enabled = True
    versioning = []
