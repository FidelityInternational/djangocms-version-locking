from cms.test_utils.testcases import CMSTestCase

from djangocms_versioning import constants

from djangocms_version_locking.test_utils import factories


class TestVersionsLockTestCase(CMSTestCase):

    def test_version_is_locked_for_draft(self):
        """
        A version lock is present when a content version is in a draft state
        """
        draft_version = factories.PollVersionFactory(state=constants.DRAFT)

        self.assertTrue(hasattr(draft_version, 'versionlock'))

    def test_version_is_unlocked_for_published(self):
        """
        A version lock is not present when a content version is in a published state
        """
        published_version = factories.PollVersionFactory(state=constants.PUBLISHED)

        self.assertFalse(hasattr(published_version, 'versionlock'))


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
        A version lock is created for a new draft version copied from a draft version
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