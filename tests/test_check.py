from cms.models.fields import PlaceholderRelationField
from cms.test_utils.testcases import CMSTestCase

from djangocms_versioning.constants import ARCHIVED
from djangocms_versioning.test_utils.factories import (
    FancyPollFactory,
    PageVersionFactory,
    PlaceholderFactory,
)

from djangocms_version_locking.helpers import (
    placeholder_content_is_unlocked_for_user,
)


class CheckLockTestCase(CMSTestCase):

    def test_check_no_lock(self):
        user = self.get_superuser()
        version = PageVersionFactory(state=ARCHIVED)
        placeholder = PlaceholderFactory(source=version.content)

        self.assertTrue(placeholder_content_is_unlocked_for_user(placeholder, user))

    def test_check_locked_for_the_same_user(self):
        user = self.get_superuser()
        version = PageVersionFactory(created_by=user)
        placeholder = PlaceholderFactory(source=version.content)

        self.assertTrue(placeholder_content_is_unlocked_for_user(placeholder, user))

    def test_check_locked_for_the_other_user(self):
        user1 = self.get_superuser()
        user2 = self.get_standard_user()
        version = PageVersionFactory(created_by=user1)
        placeholder = PlaceholderFactory(source=version.content)

        self.assertFalse(placeholder_content_is_unlocked_for_user(placeholder, user2))

    def test_check_no_lock_for_unversioned_model(self):
        user2 = self.get_standard_user()
        placeholder = PlaceholderFactory(source=FancyPollFactory())

        self.assertTrue(placeholder_content_is_unlocked_for_user(placeholder, user2))


class CheckInjectTestCase(CMSTestCase):

    def test_lock_check_is_injected_into_default_checks(self):
        self.assertIn(
            placeholder_content_is_unlocked_for_user,
            PlaceholderRelationField.default_checks,
        )
