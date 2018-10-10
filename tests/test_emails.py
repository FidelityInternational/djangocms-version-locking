from django.contrib.auth.models import Permission
from django.core import mail
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from cms.test_utils.testcases import CMSTestCase
from cms.utils import get_current_site

from djangocms_versioning.cms_config import VersioningCMSConfig
from djangocms_versioning.test_utils import factories

from djangocms_version_locking.utils import get_absolute_url


class VersionLockNotificationEmailsTestCase(CMSTestCase):

    def setUp(self):
        self.superuser = self.get_superuser()
        self.user_author = self._create_user("author", is_staff=True, is_superuser=False)
        self.user_has_no_perms = self._create_user("user_has_no_perms", is_staff=True, is_superuser=False)
        self.user_has_unlock_perms = self._create_user("user_has_unlock_perms", is_staff=True, is_superuser=False)
        self.versionable = VersioningCMSConfig.versioning[0]

        # Set permissions
        delete_permission = Permission.objects.get(codename='delete_versionlock')
        self.user_has_unlock_perms.user_permissions.add(delete_permission)

    def test_notify_version_author_version_unlocked_email_sent_for_different_user(self):
        """
        The user unlocking a version that is authored buy a different user
        should be sent a notification email
        """
        draft_version = factories.PageVersionFactory(content__template="", created_by=self.user_author)
        draft_unlock_url = self.get_admin_url(self.versionable.version_model_proxy,
                                              'unlock', draft_version.pk)

        # Check that no emails exist
        self.assertEqual(len(mail.outbox), 0)

        # Unlock the version with a different user with unlock permissions
        with self.login_user_context(self.user_has_unlock_perms):
            self.client.post(draft_unlock_url, follow=True)

        site = get_current_site()
        expected_subject = "[Django CMS] ({site_name}) {page_title} - {description}".format(
            site_name=site.name,
            page_title=draft_version.content,
            description=_("Unlocked"),
        )
        expected_body = "The following draft version has been unlocked by {by_user} for their use.".format(
            by_user=self.user_has_unlock_perms
        )
        expected_version_url = reverse(
            'admin:cms_placeholder_render_object_preview',
            args=(draft_version.content_type_id, draft_version.object_id),
        )
        expected_version_url = get_absolute_url(expected_version_url)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, expected_subject)
        self.assertEqual(mail.outbox[0].to[0], self.user_author.email)
        self.assertTrue(expected_body in mail.outbox[0].body)
        self.assertTrue(expected_version_url in mail.outbox[0].body)

    def test_notify_version_author_version_unlocked_email_not_sent_for_different_user(self):
        """
        The user unlocking a version that authored the version should not be
        sent a notification email
        """
        draft_version = factories.PageVersionFactory(content__template="", created_by=self.user_author)
        draft_unlock_url = self.get_admin_url(self.versionable.version_model_proxy,
                                              'unlock', draft_version.pk)

        # Check that no emails exist
        self.assertEqual(len(mail.outbox), 0)

        # Unlock the version the same user who authored it
        with self.login_user_context(self.user_author):
            self.client.post(draft_unlock_url, follow=True)

        # Check that no emails still exist
        self.assertEqual(len(mail.outbox), 0)
