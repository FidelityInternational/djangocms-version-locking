from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

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
        btn_name = format_html(
            '<span style="vertical-align:middle;position:relative;top:-1px" class="cms-icon cms-icon-lock"></span>{name}',  # noqa: E501
            name=_('Edit'),
        )
        edit_button = find_toolbar_buttons(btn_name, toolbar.toolbar)[0]

        self.assertEqual(edit_button.name, btn_name)
        self.assertEqual(edit_button.url, 'javascript:void(0)')
        self.assertTrue(edit_button.disabled)
        self.assertListEqual(
            edit_button.extra_classes,
            ['cms-btn-action', 'cms-version-locking-btn-icon']
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

    def test_edit_button_when_content_is_locked_users_full_name_used(self):
        user = self.get_superuser()
        user.first_name = "Firstname"
        user.last_name = "Lastname"
        user.save()
        user_2 = UserFactory(
            is_staff=True,
            is_superuser=True,
            username='admin2',
            email='admin2@123.com',
        )
        version = PageVersionFactory(created_by=user)

        toolbar = get_toolbar(version.content, user_2, content_mode=True)
        toolbar.post_template_populate()
        btn_name = format_html(
            '<span style="vertical-align:middle;position:relative;top:-1px" class="cms-icon cms-icon-lock"></span>{name}',  # noqa: E501
            name=_('Edit'),
        )
        edit_button = find_toolbar_buttons(btn_name, toolbar.toolbar)[0]

        self.assertEqual(edit_button.html_attributes, {'title': "Locked with {}".format(user.get_full_name())})

    def test_edit_button_when_content_is_locked_users_username_used(self):
        user = self.get_superuser()
        user.first_name = ""
        user.last_name = ""
        user.save()
        user_2 = UserFactory(
            is_staff=True,
            is_superuser=True,
            username='admin2',
            email='admin2@123.com',
        )
        version = PageVersionFactory(created_by=user)

        toolbar = get_toolbar(version.content, user_2, content_mode=True)
        toolbar.post_template_populate()
        btn_name = format_html(
            '<span style="vertical-align:middle;position:relative;top:-1px" class="cms-icon cms-icon-lock"></span>{name}',  # noqa: E501
            name=_('Edit'),
        )
        edit_button = find_toolbar_buttons(btn_name, toolbar.toolbar)[0]

        self.assertEqual(edit_button.html_attributes, {'title': "Locked with {}".format(user.username)})
