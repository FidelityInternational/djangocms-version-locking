from cms.models.fields import PlaceholderRelationField
from cms.test_utils.testcases import CMSTestCase

from djangocms_versioning.test_utils.factories import (
    PageVersionFactory,
    PlaceholderFactory,
)

from djangocms_version_locking.check import content_is_not_locked
from djangocms_version_locking.models import VersionLock


class CheckLockTestCase(CMSTestCase):

    def test_check_no_lock(self):
        user = self.get_superuser()
        version = PageVersionFactory()
        placeholder = PlaceholderFactory(source=version.content)

        self.assertTrue(content_is_not_locked(placeholder, user))

    def test_check_locked_for_the_same_user(self):
        user = self.get_superuser()
        version = PageVersionFactory()
        placeholder = PlaceholderFactory(source=version.content)
        VersionLock.objects.create(
            version=version,
            created_by=user,
        )

        self.assertTrue(content_is_not_locked(placeholder, user))

    def test_check_locked_for_the_other_user(self):
        user1 = self.get_superuser()
        user2 = self.get_standard_user()
        version = PageVersionFactory()
        placeholder = PlaceholderFactory(source=version.content)
        VersionLock.objects.create(
            version=version,
            created_by=user1,
        )

        self.assertFalse(content_is_not_locked(placeholder, user2))


class CheckInjectTestCase(CMSTestCase):

    def test_lock_check_is_injected_into_default_checks(self):
        self.assertIn(
            content_is_not_locked,
            PlaceholderRelationField.default_checks,
        )
