from unittest.mock import Mock, patch

from django.contrib import admin

from cms.test_utils.testcases import CMSTestCase

import djangocms_version_locking.helpers
from djangocms_version_locking.admin import VersionLockAdminMixin
from djangocms_version_locking.helpers import (
    replace_admin_for_models,
    version_lock_admin_factory,
)



from django.apps import apps


from djangocms_version_locking.models import Version
from djangocms_version_locking.test_utils import factories
from djangocms_version_locking.test_utils.polls.cms_config import PollsCMSConfig
from djangocms_version_locking.test_utils.polls.models import PollContent


# Test When a version is in draft a version lock is created
# Test When a version is in publish a version lock is deleted

# Test When a version is in draft and a version lock does not exist the delete is ok


class MytestCase(CMSTestCase):

    def setUp(self):
        self.model = Poll
        self.site = admin.AdminSite()

    def test_version_is_locked_on_copy(self):
        """
        TODO
        """

        version = factories.PollVersionFactory()
        user = factories.UserFactory()

        assertTrue(False)

