from django.test import RequestFactory

from cms.test_utils.testcases import CMSTestCase
from cms.toolbar.toolbar import CMSToolbar
from cms.toolbar.utils import get_object_preview_url

from djangocms_versioning.cms_toolbars import VersioningToolbar
from djangocms_versioning.test_utils.factories import (
    PageVersionFactory,
    UserFactory,
)


class VersionToolbarOverrideTestCase(CMSTestCase):

    def _get_toolbar(self, content_obj, user, **kwargs):
        """Helper method to set up the toolbar
        """
        request = RequestFactory().get('/')
        request.user = user
        request.session = {}
        request.current_page = getattr(content_obj, 'page', None)
        request.toolbar = CMSToolbar(request)
        # Get the toolbar class to use
        if kwargs.get('toolbar_class', False):
            toolbar_class = kwargs.get('toolbar_class')
        else:
            toolbar_class = VersioningToolbar
        toolbar = toolbar_class(
            request,
            toolbar=request.toolbar,
            is_current_app=True,
            app_path='/',
        )
        toolbar.toolbar.obj = content_obj
        if kwargs.get('edit_mode', False):
            toolbar.toolbar.edit_mode_active = True
            toolbar.toolbar.content_mode_active = False
            toolbar.toolbar.structure_mode_active = False
        elif kwargs.get('preview_mode', False):
            toolbar.toolbar.edit_mode_active = False
            toolbar.toolbar.content_mode_active = True
            toolbar.toolbar.structure_mode_active = False
        elif kwargs.get('structure_mode', False):
            toolbar.toolbar.edit_mode_active = False
            toolbar.toolbar.content_mode_active = False
            toolbar.toolbar.structure_mode_active = True
        toolbar.populate()
        return toolbar

    def _find_buttons(self):
        #TODO
        pass

    def test_not_render_edit_button_when_not_content_mode(self):
        user = self.get_superuser()
        version = PageVersionFactory(created_by=user)

        toolbar = self._get_toolbar(version.content, user, edit_mode=True)
        toolbar.post_template_populate()
        buttons = toolbar.toolbar.get_right_items()[0].buttons
        self.assertListEqual(
            [b for b in buttons if b.name == 'Edit'],
            []
        )

    def test_disable_edit_button_when_content_is_locked(self):
        user = self.get_superuser()
        user_2 = UserFactory(
            is_staff=True,
            is_superuser=True,
            username='admin2',
            email='admin2@123.com',
        )
        version = PageVersionFactory(created_by=user)

        toolbar = self._get_toolbar(version.content, user_2, content_mode=True)
        toolbar.post_template_populate()
        edit_button = toolbar.toolbar.get_right_items()[0].buttons[0]
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

        toolbar = self._get_toolbar(version.content, user, content_mode=True)
        toolbar.post_template_populate()
        edit_button = toolbar.toolbar.get_right_items()[0].buttons[0]
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
