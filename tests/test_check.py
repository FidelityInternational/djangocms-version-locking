from cms.models.fields import PlaceholderRelationField
from cms.test_utils.testcases import CMSTestCase

from djangocms_versioning.test_utils.factories import (
    PageVersionFactory,
    PlaceholderFactory,
)

from djangocms_version_locking.helpers import placeholder_content_is_unlocked
from djangocms_version_locking.models import VersionLock


class CheckLockTestCase(CMSTestCase):

    def test_check_no_lock(self):
        user = self.get_superuser()
        version = PageVersionFactory()
        placeholder = PlaceholderFactory(source=version.content)

        self.assertTrue(placeholder_content_is_unlocked(placeholder, user))

    def test_check_locked_for_the_same_user(self):
        user = self.get_superuser()
        version = PageVersionFactory()
        placeholder = PlaceholderFactory(source=version.content)
        VersionLock.objects.create(
            version=version,
            created_by=user,
        )

        self.assertTrue(placeholder_content_is_unlocked(placeholder, user))

    def test_check_locked_for_the_other_user(self):
        user1 = self.get_superuser()
        user2 = self.get_standard_user()
        version = PageVersionFactory()
        placeholder = PlaceholderFactory(source=version.content)
        VersionLock.objects.create(
            version=version,
            created_by=user1,
        )

        self.assertFalse(placeholder_content_is_unlocked(placeholder, user2))


class CheckInjectTestCase(CMSTestCase):

    def test_lock_check_is_injected_into_default_checks(self):
        self.assertIn(
            placeholder_content_is_unlocked,
            PlaceholderRelationField.default_checks,
        )
