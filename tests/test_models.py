from cms.test_utils.testcases import CMSTestCase

from djangocms_versioning.constants import DRAFT, PUBLISHED

from djangocms_versioning import constants
from djangocms_versioning.models import Version

from djangocms_version_locking.test_utils import factories
from djangocms_version_locking.test_utils.polls.cms_config import PollsCMSConfig


class TestVersionsLockTestCase(CMSTestCase):

    def setUp(self):
        self.versionable = PollsCMSConfig.versioning[0]

    def test_version_is_locked_for_draft(self):
        """
        A version lock is present when a content version is in a draft state
        """
        draft_version = factories.PollVersionFactory(state=DRAFT)

        self.assertTrue(hasattr(draft_version, 'versionlock'))

    def test_version_is_unlocked_for_publishing(self):
        """
        A version lock is not present when a content version is in a published or unpublished state
        """
        poll_version = factories.PollVersionFactory(state=constants.DRAFT)
        publish_url = self.get_admin_url(self.versionable.version_model_proxy, 'publish', poll_version.pk)
        unpublish_url = self.get_admin_url(self.versionable.version_model_proxy, 'unpublish', poll_version.pk)
        user = self.get_staff_user_with_no_permissions()

        with self.login_user_context(user):
            response = self.client.post(publish_url)

        updated_poll_version = Version.objects.get(pk=poll_version.pk)

        # The state is now PUBLISHED
        self.assertEqual(updated_poll_version.state, constants.PUBLISHED)
        # Version lock does not exist
        self.assertFalse(hasattr(updated_poll_version, 'versionlock'))

        with self.login_user_context(user):
            response = self.client.post(unpublish_url)

        updated_poll_version = Version.objects.get(pk=poll_version.pk)

        # The state is now UNPUBLISHED
        self.assertEqual(updated_poll_version.state, constants.UNPUBLISHED)
        # Version lock does not exist
        self.assertFalse(hasattr(updated_poll_version, 'versionlock'))

    def test_version_is_unlocked_for_archived(self):
        """
        A version lock is not present when a content version is in an archived state
        """
        poll_version = factories.PollVersionFactory(state=constants.DRAFT)
        archive_url = self.get_admin_url(self.versionable.version_model_proxy, 'archive', poll_version.pk)
        user = self.get_staff_user_with_no_permissions()

        with self.login_user_context(user):
            response = self.client.post(archive_url)

        updated_poll_version = Version.objects.get(pk=poll_version.pk)

        # The state is now ARCHIVED
        self.assertEqual(updated_poll_version.state, constants.ARCHIVED)
        # Version lock does not exist
        self.assertFalse(hasattr(updated_poll_version, 'versionlock'))


class TestVersionCopyLocks(CMSTestCase):

    def test_draft_version_copy_creates_draft_lock(self):
        """
        A version lock is created for a new draft version copied from a draft version
        """
        user = factories.UserFactory()
        draft_version = factories.PollVersionFactory(state=constants.DRAFT)
        new_version = draft_version.copy(user)

        self.assertTrue(hasattr(new_version, 'versionlock'))

    def test_published_version_copy_creates_draft_lock(self):
        """
        A version lock is created for a published version copied from a draft version
        """
        user = factories.UserFactory()
        published_version = factories.PollVersionFactory(state=constants.PUBLISHED)
        new_version = published_version.copy(user)

        self.assertTrue(hasattr(new_version, 'versionlock'))

    def test_version_copy_adds_correct_locked_user(self):
        """
        A copied version creates a lock for the user that copied the version.
        The users should not be the same.
        """
        original_user = factories.UserFactory()
        original_version = factories.PollVersionFactory(created_by=original_user)
        copy_user = factories.UserFactory()
        copied_version = original_version.copy(copy_user)

        self.assertNotEqual(original_user, copy_user)
        self.assertEqual(original_version.versionlock.created_by, original_user)
        self.assertEqual(copied_version.versionlock.created_by, copy_user)