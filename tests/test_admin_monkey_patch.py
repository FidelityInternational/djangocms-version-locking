from cms.test_utils.testcases import CMSTestCase

from django.contrib.auth.models import Permission
from django.template.loader import render_to_string

from djangocms_versioning import constants
from djangocms_versioning.models import Version

from djangocms_version_locking.test_utils import factories
from djangocms_version_locking.test_utils.polls.cms_config import PollsCMSConfig


class VersionLockUnlockTestCase(CMSTestCase):

    """
    FIXME: Possible that a user can have the ability to create a version and publish it but there is an issue where the
            permissiosn to delete a version lock may prevent them from completing the task.

            It's ok as long as the permssion isn't enforced on the delete on publish which it doesn't currently!!
    """

    def setUp(self):
        self.superuser = self.get_superuser()
        self.user_author = self._create_user("author", is_staff=True, is_superuser=False)
        self.user_has_no_perms = self._create_user("user_has_no_perms", is_staff=True, is_superuser=False)
        self.user_has_unlock_perms = self._create_user("user_has_unlock_perms", is_staff=True, is_superuser=False)
        self.versionable = PollsCMSConfig.versioning[0]

        self.user_has_unlock_perms.user_permissions.add(Permission.objects.get(codename='delete_versionlock'))
        self.user_author = self._create_user("author", is_staff=True, is_superuser=False)

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

        self.assertEqual(response.status_code, 200)

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
