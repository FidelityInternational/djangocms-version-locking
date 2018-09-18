from unittest.mock import Mock

from django.core.exceptions import ImproperlyConfigured

from cms.test_utils.testcases import CMSTestCase

from djangocms_version_locking.cms_config import VersionLockingCMSExtension


class VersionLockExtensionUnitTestCase(CMSTestCase):

    def test_raises_exception_if_versioning_not_implemented(self):
        """
        If the versioning attribute has not been specified,
        an ImproperlyConfigured exception is raised
        """
        extensions = VersionLockingCMSExtension()
        cms_config = Mock(
            spec=[],
            djangocms_versioning_enabled=False,
            version_lock_models=[]
        )

        with self.assertRaises(ImproperlyConfigured):
            extensions.handle_settings(cms_config)

    def test_raises_exception_if_version_lock_models_not_iterable(self):
        """
        ImproperlyConfigured exception is raised if
        version_lock_models setting is not an iterable
        """
        extensions = VersionLockingCMSExtension()
        cms_config_1 = Mock(
            spec=[],
            djangocms_versioning_enabled=True,
            version_lock_models="some other value"
        )
        cms_config_2 = Mock(
            spec=[],
            djangocms_versioning_enabled=True,
            version_lock_models={}
        )
        cms_config_3 = Mock(
            spec=[],
            djangocms_versioning_enabled=True,
            version_lock_models=()
        )

        with self.assertRaises(ImproperlyConfigured):
            extensions.handle_settings(cms_config_1)

        with self.assertRaises(ImproperlyConfigured):
            extensions.handle_settings(cms_config_2)

        with self.assertRaises(ImproperlyConfigured):
            extensions.handle_settings(cms_config_3)