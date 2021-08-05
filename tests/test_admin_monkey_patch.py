from unittest import skip

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.test import RequestFactory

from cms.test_utils.testcases import CMSTestCase

from djangocms_version_locking.models import VersionLock
from djangocms_version_locking.test_utils import factories
from djangocms_version_locking.test_utils.polls.cms_config import (
    PollsCMSConfig,
)
from djangocms_version_locking.test_utils.polls.models import PollContent
from djangocms_versioning import constants
from djangocms_versioning.admin import ExtendedVersionAdminMixin
from djangocms_versioning.helpers import version_list_url
from djangocms_versioning.models import Version


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

    @classmethod
    def setUpTestData(cls):
        cls.versionable = PollsCMSConfig.versioning[0]
        cls.default_permissions = ["change_pollcontentversion"]

    def setUp(self):
        self.superuser = self.get_superuser()
        self.user_author = self._create_user(
            "author",
            is_staff=True,
            permissions=self.default_permissions,
        )
        self.user_has_no_unlock_perms = self._create_user(
            "user_has_no_unlock_perms",
            is_staff=True,
            permissions=self.default_permissions,
        )
        self.user_has_unlock_perms = self._create_user(
            "user_has_unlock_perms",
            is_staff=True,
            permissions=["delete_versionlock"] + self.default_permissions,
        )

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

        with self.login_user_context(self.user_has_no_unlock_perms):
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

    @skip("Requires clarification if this is still a valid requirement!")
    def test_unlock_link_not_present_for_author(self):
        # FIXME: May be redundant now as this requirement was probably removed at a later date due
        #  to the fact that an author may be asked to unlock their version for someone else to use!
        author = self.get_superuser()
        poll_version = factories.PollVersionFactory(state=constants.DRAFT, created_by=author)
        changelist_url = version_list_url(poll_version.content)
        unlock_url = self.get_admin_url(self.versionable.version_model_proxy, 'unlock', poll_version.pk)
        unlock_control = render_to_string(
            'djangocms_version_locking/admin/unlock_icon.html',
            {'unlock_url': unlock_url}
        )

        with self.login_user_context(author):
            response = self.client.get(changelist_url)

        self.assertNotContains(response, unlock_control, html=True)

    def test_unlock_link_not_present_for_user_with_no_unlock_privileges(self):
        poll_version = factories.PollVersionFactory(state=constants.DRAFT, created_by=self.user_author)
        changelist_url = version_list_url(poll_version.content)
        unlock_url = self.get_admin_url(self.versionable.version_model_proxy, 'unlock', poll_version.pk)
        unlock_control = render_to_string(
            'djangocms_version_locking/admin/unlock_icon.html',
            {'unlock_url': unlock_url}
        )

        with self.login_user_context(self.user_has_no_unlock_perms):
            response = self.client.post(changelist_url)

        self.assertNotContains(response, unlock_control, html=True)

    def test_unlock_link_present_for_user_with_privileges(self):
        poll_version = factories.PollVersionFactory(state=constants.DRAFT, created_by=self.user_author)
        changelist_url = version_list_url(poll_version.content)
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
        changelist_url = version_list_url(draft_version.content)

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
        updated_draft_edit_url = self.get_admin_url(
            self.versionable.version_model_proxy,
            'edit_redirect', updated_draft_version.pk
        )

        # The version is still owned by the author
        self.assertTrue(updated_draft_version.created_by, self.user_author)
        # The version lock does not exist
        self.assertFalse(hasattr(updated_draft_version, 'versionlock'))

        # Visit the edit page with a user without unlock permissions
        with self.login_user_context(self.user_has_no_unlock_perms):
            self.client.post(updated_draft_edit_url)

        updated_draft_version = Version.objects.get(pk=draft_version.pk)

        # The version is now owned by the user with no permissions
        self.assertTrue(updated_draft_version.created_by, self.user_has_no_unlock_perms)
        # The version lock exists and is now owned by the user with no permissions
        self.assertEqual(updated_draft_version.versionlock.created_by, self.user_has_no_unlock_perms)


class VersionLockEditActionStateTestCase(CMSTestCase):

    def setUp(self):
        self.superuser = self.get_superuser()
        self.user_author = self._create_user("author", is_staff=True, is_superuser=False)
        self.versionable = PollsCMSConfig.versioning[0]
        self.version_admin = admin.site._registry[self.versionable.version_model_proxy]

    def test_edit_action_link_enabled_state(self):
        """
        The edit action is active
        """
        version = factories.PollVersionFactory(created_by=self.user_author)
        author_request = RequestFactory()
        author_request.user = self.user_author
        otheruser_request = RequestFactory()
        otheruser_request.user = self.superuser

        actual_enabled_state = self.version_admin._get_edit_link(version, author_request)

        self.assertNotIn("inactive", actual_enabled_state)

    def test_edit_action_link_disabled_state(self):
        """
        The edit action is disabled for a different user to the locked user
        """
        version = factories.PollVersionFactory(created_by=self.user_author)
        author_request = RequestFactory()
        author_request.user = self.user_author
        otheruser_request = RequestFactory()
        otheruser_request.user = self.superuser
        actual_disabled_state = self.version_admin._get_edit_link(version, otheruser_request)

        self.assertIn("inactive", actual_disabled_state)


class VersionLockMediaMonkeyPatchTestCase(CMSTestCase):

    def setUp(self):
        self.superuser = self.get_superuser()
        self.model = PollContent
        self.site = admin.AdminSite()
        self.admin_class = type("TestAdmin", (ExtendedVersionAdminMixin, admin.ModelAdmin,), {})

    def test_version_locking_css_media_loaded(self):
        """
        The version locking css media is loaded on the page
        """
        poll_version = factories.PollVersionFactory(created_by=self.superuser)
        changelist_url = version_list_url(poll_version.content)
        css_file = "djangocms_version_locking/css/version-locking.css"

        with self.login_user_context(self.superuser):
            response = self.client.post(changelist_url)

        self.assertContains(response, css_file)

    def test_version_locking_extended_admin_css_media_loaded(self):
        """
        The version locking css media for extended version admin is loaded on the page
        """
        admin.site.unregister(PollContent)

        class AdminExtended(ExtendedVersionAdminMixin, admin.ModelAdmin):
            pass

        admin.site.register(PollContent, AdminExtended)
        poll_version = factories.PollVersionFactory(created_by=self.superuser)
        changelist_url = version_list_url(poll_version.content)
        css_file = "djangocms_version_locking/css/version-locking.css"

        with self.login_user_context(self.superuser):
            response = self.client.post(changelist_url)

        self.assertContains(response, css_file)


class ExtendedAdminVersionLockMonkeyPatchActionStateTestCase(CMSTestCase):

    def setUp(self):
        admin.site.unregister(PollContent)

        class AdminExtended(ExtendedVersionAdminMixin, admin.ModelAdmin):
            pass

        admin.site.register(PollContent, AdminExtended)
        self.superuser = self.get_superuser()
        self.user_author = self._create_user("author", is_staff=True, is_superuser=False)
        self.versionable = PollsCMSConfig.versioning[0]
        self.version_admin = admin.site._registry[self.versionable.version_model_proxy]

    def test_edit_action_link_enabled_state(self):
        """
        The edit action is active for given user
        """
        version = factories.PollVersionFactory(created_by=self.user_author)
        author_request = RequestFactory()
        author_request.user = self.user_author
        otheruser_request = RequestFactory()
        otheruser_request.user = self.superuser

        actual_enabled_state = self.version_admin._get_edit_link(version, author_request)

        self.assertNotIn("inactive", actual_enabled_state)

    def test_edit_action_link_disabled_state(self):
        """
        The edit action is disabled for a different user to the locked user
        """
        version = factories.PollVersionFactory(created_by=self.user_author)
        author_request = RequestFactory()
        author_request.user = self.user_author
        otheruser_request = RequestFactory()
        otheruser_request.user = self.superuser
        actual_disabled_state = self.version_admin._get_edit_link(version, otheruser_request)

        self.assertIn("inactive", actual_disabled_state)

class ExtendedAdminVersionFieldMonkeyPatchTestCase(CMSTestCase):

    def setUp(self):
        self.superuser = self.get_superuser()

    def test_extended_admin_monkey_patch_list_display_locked(self):
        """
        Monkey patch should add lock values to admin menus which implement
        the ExtendedVersionAdminMixin
        """
        class ExtendedPollAdmin(ExtendedVersionAdminMixin, admin.ModelAdmin):
            """
            Admin class for PollContent that implements extended versioning functionality
            """
            pass
        admin.site.unregister(PollContent)
        admin.site.register(PollContent, ExtendedPollAdmin)
        version = factories.PollVersionFactory(created_by=self.superuser)
        request = self.get_request("/")

        version_admin = admin.site._registry[type(version.content)]
        list_display = version_admin.get_list_display(request)

        # List display field should have been added by monkeypatch
        self.assertIn('locked', list_display)

        changelist_url = version_list_url(version.content)

        with self.login_user_context(self.superuser):
            response = self.client.post(changelist_url)

        # Lock options should be rendered rendered
        self.assertContains(
            response, 'td class="field-locked">\n<span class="cms-version-locked-status-icon" title="Locked">'
        )

        # The monkey patch should have replaced the get_list_display method with the method provided
        self.assertIn('ExtendedAdminVersionFieldMonkeyPatchTestCase', str(version_admin.get_list_display))
