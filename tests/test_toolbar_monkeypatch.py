from cms.test_utils.testcases import CMSTestCase

from djangocms_versioning.test_utils.factories import (
    PageVersionFactory,
    UserFactory,
)

from djangocms_version_locking.test_utils.test_helpers import (
    find_toolbar_buttons,
    get_toolbar,
    toolbar_button_exists,
)


class VersionToolbarOverrideTestCase(CMSTestCase):

    def test_not_render_edit_button_when_not_content_mode(self):
        user = self.get_superuser()
        version = PageVersionFactory(created_by=user)

        toolbar = get_toolbar(version.content, user, edit_mode=True)
        toolbar.post_template_populate()

        self.assertFalse(toolbar_button_exists('Edit', toolbar.toolbar))

    def test_disable_edit_button_when_content_is_locked(self):
        user = self.get_superuser()
        user_2 = UserFactory(
            is_staff=True,
            is_superuser=True,
            username='admin2',
            email='admin2@123.com',
        )
        version = PageVersionFactory(created_by=user)

        toolbar = get_toolbar(version.content, user_2, content_mode=True)
        toolbar.post_template_populate()
        edit_button = find_toolbar_buttons('Edit', toolbar.toolbar)[0]

        self.assertEqual(edit_button.name, 'Edit')
        self.assertEqual(edit_button.url, '')
        self.assertTrue(edit_button.disabled)
        self.assertListEqual(
            edit_button.extra_classes,
            ['cms-btn-action', 'cms-icon', 'cms-icon-lock']
        )

    def test_enable_edit_button_when_content_is_locked(self):
        from django.apps import apps
        from cms.models import Page

        user = self.get_superuser()
        version = PageVersionFactory(created_by=user)

        toolbar = get_toolbar(version.content, user, content_mode=True)
        toolbar.post_template_populate()
        edit_button = find_toolbar_buttons('Edit', toolbar.toolbar)[0]

        self.assertEqual(edit_button.name, 'Edit')

        cms_extension = apps.get_app_config('djangocms_versioning').cms_extension
        versionable = cms_extension.versionables_by_grouper[Page]
        admin_url = self.get_admin_url(
            versionable.version_model_proxy, 'edit_redirect', version.pk
        )
        self.assertEqual(edit_button.url, admin_url)
        self.assertFalse(edit_button.disabled)
        self.assertListEqual(
            edit_button.extra_classes,
            ['cms-btn-action', 'cms-versioning-js-edit-btn']
        )
