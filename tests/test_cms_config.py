from unittest import skip
from unittest.mock import Mock

from django.core.exceptions import ImproperlyConfigured

from cms.test_utils.testcases import CMSTestCase

from djangocms_version_locking.cms_config import VersionLockingCMSExtension
from djangocms_version_locking.test_utils.polls.models import PollContent


class VersionLockExtensionUnitTestCase(CMSTestCase):
    def test_raises_exception_if_versioning_not_implemented(self):
        """
        If the versioning attribute has not been specified,
        an ImproperlyConfigured exception is raised
        """
        extensions = VersionLockingCMSExtension()
        cms_config = Mock(
            spec=[], djangocms_versioning_enabled=False, version_lock_models=[]
        )

        with self.assertRaises(ImproperlyConfigured):
            extensions.handle_settings(cms_config)
