from cms.test_utils.testcases import CMSTestCase

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string

from djangocms_versioning import constants
from djangocms_versioning.models import Version

from djangocms_version_locking.models import VersionLock
from djangocms_version_locking.test_utils import factories
from djangocms_version_locking.test_utils.polls.cms_config import PollsCMSConfig


def _content_has_lock(content):
    """
    Check for a lock entry from content
    """
    try:
        VersionLock.objects.get(
            version__content_type=ContentType.objects.get_for_model(content),
            version__object_id=content.pk,
        )
    except VersionLock.DoesNotExist:
        return False
    return True


class VersionLockUnlockTestCase(CMSTestCase):

    def setUp(self):
        self.superuser = self.get_superuser()
        self.user_author = self._create_user("author", is_staff=True, is_superuser=False)
        self.user_has_no_perms = self._create_user("user_has_no_perms", is_staff=True, is_superuser=False)
        self.user_has_unlock_perms = self._create_user("user_has_unlock_perms", is_staff=True, is_superuser=False)
        self.versionable = PollsCMSConfig.versioning[0]

        # Set permissions
        delete_permission = Permission.objects.get(codename='delete_versionlock')
        self.user_has_unlock_perms.user_permissions.add(delete_permission)

    def test_unlock_view_redirects_404_when_not_draft(self):
        poll_version = factories.PollVersionFactory(state=constants.PUBLISHED, created_by=self.superuser)
        unlock_url = self.get_admin_url(self.versionable.version_model_proxy, 'unlock', poll_version.pk)

        # 404 when not in draft
        with self.login_user_context(self.superuser):
            response = self.client.post(unlock_url, follow=True)

        self.assertEqual(response.status_code, 404)

    def test_unlock_view_not_possible_for_user_with_no_permissions(self):
        poll_version = factories.PollVersionFactory(state=constants.DRAFT, created_by=self.user_author)
        unlock_url = self.get_admin_url(self.versionable.version_model_proxy, 'unlock', poll_version.pk)
        
        with self.login_user_context(self.user_has_no_perms):
            response = self.client.post(unlock_url, follow=True)

        self.assertEqual(response.status_code, 403)

        # Fetch the latest state of this version
        updated_poll_version = Version.objects.get(pk=poll_version.pk)

        # The version is still locked
        self.assertTrue(hasattr(updated_poll_version, 'versionlock'))
        # The author is unchanged
        self.assertEqual(updated_poll_version.versionlock.created_by, self.user_author)

    def test_unlock_view_possible_for_user_with_permissions(self):
        poll_version = factories.PollVersionFactory(state=constants.DRAFT, created_by=self.user_author)
        unlock_url = self.get_admin_url(self.versionable.version_model_proxy, 'unlock', poll_version.pk)

        with self.login_user_context(self.user_has_unlock_perms):
            response = self.client.post(unlock_url, follow=True)

        self.assertEqual(response.status_code, 200)

        # Fetch the latest state of this version
        updated_poll_version = Version.objects.get(pk=poll_version.pk)

        # The version is not locked
        self.assertFalse(hasattr(updated_poll_version, 'versionlock'))

    def test_unlock_link_not_present_for_author(self):
        poll_version = factories.PollVersionFactory(state=constants.DRAFT, created_by=self.user_author)
        changelist_url = self.get_admin_url(self.versionable.version_model_proxy, 'changelist') \
              + '?grouper=' + str(poll_version.content.poll.pk)
        unlock_url = self.get_admin_url(self.versionable.version_model_proxy, 'unlock', poll_version.pk)
        unlock_control = render_to_string(
            'djangocms_version_locking/admin/unlock_icon.html',
            {'unlock_url': unlock_url}
        )

        with self.login_user_context(self.user_author):
            response = self.client.post(changelist_url)

        self.assertNotContains(response, unlock_control, html=True)

    def test_unlock_link_not_present_for_user_with_no_unlock_privileges(self):
        poll_version = factories.PollVersionFactory(state=constants.DRAFT, created_by=self.user_author)
        changelist_url = self.get_admin_url(self.versionable.version_model_proxy, 'changelist') \
              + '?grouper=' + str(poll_version.content.poll.pk)
        unlock_url = self.get_admin_url(self.versionable.version_model_proxy, 'unlock', poll_version.pk)
        unlock_control = render_to_string(
            'djangocms_version_locking/admin/unlock_icon.html',
            {'unlock_url': unlock_url}
        )

        with self.login_user_context(self.user_has_no_perms):
            response = self.client.post(changelist_url)

        self.assertNotContains(response, unlock_control, html=True)

    def test_unlock_link_present_for_user_with_privileges(self):
        poll_version = factories.PollVersionFactory(state=constants.DRAFT, created_by=self.user_author)
        changelist_url = self.get_admin_url(self.versionable.version_model_proxy, 'changelist') \
              + '?grouper=' + str(poll_version.content.poll.pk)
        unlock_url = self.get_admin_url(self.versionable.version_model_proxy, 'unlock', poll_version.pk)
        unlock_control = render_to_string(
            'djangocms_version_locking/admin/unlock_icon.html',
            {'unlock_url': unlock_url}
        )

        with self.login_user_context(self.user_has_unlock_perms):
            response = self.client.post(changelist_url)

        self.assertContains(response, unlock_control, html=True)

    def test_unlock_link_only_present_for_draft_versions(self):
        draft_version = factories.PollVersionFactory(created_by=self.user_author)
        published_version = Version.objects.create(
            content=factories.PollContentFactory(poll=draft_version.content.poll),
            created_by=factories.UserFactory(),
            state=constants.PUBLISHED
        )
        draft_unlock_url = self.get_admin_url(self.versionable.version_model_proxy, 'unlock', draft_version.pk)
        draft_unlock_control = render_to_string(
            'djangocms_version_locking/admin/unlock_icon.html',
            {'unlock_url': draft_unlock_url}
        )
        published_unlock_url = self.get_admin_url(self.versionable.version_model_proxy, 'unlock', published_version.pk)
        published_unlock_control = render_to_string(
            'djangocms_version_locking/admin/unlock_icon.html',
            {'unlock_url': published_unlock_url}
        )
        changelist_url = self.get_admin_url(self.versionable.version_model_proxy, 'changelist') \
              + '?grouper=' + str(draft_version.content.poll.pk)

        with self.login_user_context(self.superuser):
            response = self.client.post(changelist_url)

        # The draft version unlock control exists
        self.assertContains(response, draft_unlock_control, html=True)
        # The published version exists
        self.assertNotContains(response, published_unlock_control, html=True)

    def test_unlock_and_new_user_edit_creates_version_lock(self):
        """
        When a version is unlocked a different user (or the same) can then visit the edit link and take
        ownership of the version, this creates a version lock for the editing user
        """
        draft_version = factories.PollVersionFactory(created_by=self.user_author)
        draft_unlock_url = self.get_admin_url(self.versionable.version_model_proxy,
                                              'unlock', draft_version.pk)

        # The version is owned by the author
        self.assertEqual(draft_version.created_by, self.user_author)
        # The version lock exists and is owned by the author
        self.assertEqual(draft_version.versionlock.created_by, self.user_author)

        # Unlock the version with a different user with unlock permissions
        with self.login_user_context(self.user_has_unlock_perms):
            self.client.post(draft_unlock_url, follow=True)

        updated_draft_version = Version.objects.get(pk=draft_version.pk)
        updated_draft_edit_url = self.get_admin_url(self.versionable.version_model_proxy,
                                              'edit_redirect', updated_draft_version.pk)

        # The version is still owned by the author
        self.assertTrue(updated_draft_version.created_by, self.user_author)
        # The version lock does not exist
        self.assertFalse(hasattr(updated_draft_version, 'versionlock'))

        # Visit the edit page with a user without unlock permissions
        with self.login_user_context(self.user_has_no_perms):
            self.client.post(updated_draft_edit_url)

        updated_draft_version = Version.objects.get(pk=draft_version.pk)

        # The version is now owned by the user with no permissions
        self.assertTrue(updated_draft_version.created_by, self.user_has_no_perms)
        # The version lock exists and is now owned by the user with no permissions
        self.assertEqual(updated_draft_version.versionlock.created_by, self.user_has_no_perms)
