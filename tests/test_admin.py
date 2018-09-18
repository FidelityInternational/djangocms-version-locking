from unittest.mock import patch

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from cms.test_utils.testcases import CMSTestCase

from djangocms_versioning import admin as versioning_admin
from djangocms_versioning.constants import DRAFT, PUBLISHED

import djangocms_version_locking.helpers
from djangocms_version_locking.admin import VersionLockAdminMixin
from djangocms_version_locking.helpers import (
    replace_admin_for_models,
    version_lock_admin_factory,
)
from djangocms_version_locking.test_utils import factories
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
        self.hijacked_admin = versioning_admin.VersionAdmin

    def test_version_admin_contains_locked_field(self):
        """
        The locked column exists in the admin field list
        """
        self.assertIn(_("locked"), self.hijacked_admin.list_display)

    def test_version_lock_state_locked(self):
        """
        A published version does not have an entry in the locked column in the admin
        """
        published_version = factories.PollVersionFactory(state=PUBLISHED)

        self.assertEqual("", self.hijacked_admin.locked(self.hijacked_admin, published_version))

    def test_version_lock_state_unlocked(self):
        """
        A draft version does have an entry in the locked column in the admin
        """
        draft_version = factories.PollVersionFactory(state=DRAFT)

        self.assertEqual("Yes", self.hijacked_admin.locked(self.hijacked_admin, draft_version))


class AdminPermissionTestCase(CMSTestCase):

    def test_user_has_change_permission(self):
        """
        Test that the user who created the version has permission to change it
        """
        author = self.get_superuser()
        content = factories.PollVersionFactory(state=DRAFT, created_by=author)
        url = self.get_admin_url(PollContent, 'change', content.pk)

        with self.login_user_context(author):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_user_does_not_have_change_permission(self):
        """
        Test that a different user from the  user who created
        the version does not have permission to change it
        """
        author = factories.UserFactory()
        editor = self.get_superuser()
        content = factories.PollVersionFactory(state=DRAFT, created_by=author)
        url = self.get_admin_url(PollContent, 'change', content.pk)

        with self.login_user_context(editor):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 403)
