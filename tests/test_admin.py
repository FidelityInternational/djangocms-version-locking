from unittest import skip
from unittest.mock import patch

from django.contrib import admin
from django.test import RequestFactory
from django.utils.translation import gettext_lazy as _

from cms.test_utils.testcases import CMSTestCase

from djangocms_versioning import admin as versioning_admin
from djangocms_versioning.constants import DRAFT, PUBLISHED
from djangocms_versioning.models import Version

import djangocms_version_locking.helpers
from djangocms_version_locking.admin import VersionLockAdminMixin
from djangocms_version_locking.helpers import (
    replace_admin_for_models,
    version_lock_admin_factory,
)
from djangocms_version_locking.test_utils import factories
from djangocms_version_locking.test_utils.polls.cms_config import (
    PollsCMSConfig,
)
from djangocms_version_locking.test_utils.polls.models import (
    Answer,
    Poll,
    PollContent,
)


class AdminReplaceVersioningTestCase(CMSTestCase):

    def setUp(self):
        self.model = Poll
        self.site = admin.AdminSite()
        self.admin_class = type('TestAdmin', (admin.ModelAdmin, ), {})

    def test_replace_admin_on_unregistered_model(self):
        """Test that calling `replace_admin_for_models` with a model that
        isn't registered in admin is a no-op.
        """
        replace_admin_for_models([self.model], self.site)

        self.assertNotIn(self.model, self.site._registry)

    def test_replace_admin_on_registered_models_default_site(self):
        with patch.object(djangocms_version_locking.helpers, '_replace_admin_for_model') as mock:
            replace_admin_for_models([PollContent])

        mock.assert_called_with(admin.site._registry[PollContent], admin.site)

    def test_replace_admin_on_registered_models(self):
        self.site.register(self.model, self.admin_class)
        self.site.register(Answer, self.admin_class)
        models = [self.model, Answer]

        replace_admin_for_models(models, self.site)

        for model in models:
            self.assertIn(model, self.site._registry)
            self.assertIn(self.admin_class, self.site._registry[model].__class__.mro())
            self.assertIn(VersionLockAdminMixin, self.site._registry[model].__class__.mro())

    def test_replace_default_admin_on_registered_model(self):
        """Test that registering a model without specifying own
        ModelAdmin class still results in overridden admin class.
        """
        self.site.register(self.model)

        replace_admin_for_models([self.model], self.site)

        self.assertIn(self.model, self.site._registry)
        self.assertIn(VersionLockAdminMixin, self.site._registry[self.model].__class__.mro())

    def test_replace_admin_again(self):
        """Test that, if a model's admin class already subclasses
        VersionLockAdminMixin, nothing happens.
        """
        version_admin = version_lock_admin_factory(self.admin_class)
        self.site.register(self.model, version_admin)

        replace_admin_for_models([self.model], self.site)

        self.assertIn(self.model, self.site._registry)
        self.assertEqual(self.site._registry[self.model].__class__, version_admin)


class AdminLockedFieldTestCase(CMSTestCase):

    def setUp(self):
        site = admin.AdminSite()
        self.hijacked_admin = versioning_admin.VersionAdmin(Version, site)

    def test_version_admin_contains_locked_field(self):
        """
        The locked column exists in the admin field list
        """
        request = RequestFactory().get('/admin/djangocms_versioning/pollcontentversion/')
        self.assertIn(_("locked"), self.hijacked_admin.get_list_display(request))

    def test_version_lock_state_locked(self):
        """
        A published version does not have an entry in the locked column in the admin
        """
        published_version = factories.PollVersionFactory(state=PUBLISHED)

        self.assertEqual("", self.hijacked_admin.locked(published_version))

    def test_version_lock_state_unlocked(self):
        """
        A draft version does have an entry in the locked column in the  and is not empty
        """
        draft_version = factories.PollVersionFactory(state=DRAFT)

        self.assertNotEqual("", self.hijacked_admin.locked(draft_version))


class AdminPermissionTestCase(CMSTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.versionable = PollsCMSConfig.versioning[0]

    def setUp(self):
        self.superuser = self.get_superuser()
        self.user_has_change_perms = self._create_user(
            "user_has_unlock_perms",
            is_staff=True,
            permissions=["change_pollcontentversion", "delete_versionlock"],
        )

    @skip("FIXME: Oddly this test runs and passes fine locally but fails when ran in the CI!")
    def test_user_has_change_permission(self):
        """
        The user who created the version has permission to change it
        """
        content = factories.PollVersionFactory(state=DRAFT, created_by=self.user_has_change_perms)
        url = self.get_admin_url(self.versionable.version_model_proxy, 'change', content.pk)

        with self.login_user_context(self.user_has_change_perms):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    @skip("FIXME: This test should try and submit changes to the item as the form renders as readonly currently.")
    def test_user_does_not_have_change_permission(self):
        """
        A different user from the user who created
        the version does not have permission to change it
        """
        author = factories.UserFactory(is_staff=True)
        content = factories.PollVersionFactory(state=DRAFT, created_by=author)
        url = self.get_admin_url(self.versionable.version_model_proxy, 'change', content.pk)

        with self.login_user_context(self.user_has_change_perms):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 403)
