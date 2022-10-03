from cms.test_utils.testcases import CMSTestCase

from djangocms_moderation.models import ModerationRequest

from djangocms_versioning.test_utils.factories import PageVersionFactory

from djangocms_version_locking.test_utils.factories import (
    ModerationCollectionFactory,
    PollVersionFactory,
    UserFactory,
    PlaceholderFactory,
    PollPluginFactory,
)


class ModerationCollectionTestCase(CMSTestCase):

    def setUp(self):
        self.collection = ModerationCollectionFactory()
        self.user_1 = UserFactory()
        self.user_2 = UserFactory()

    def test_add_version_with_parent(self):
        page_version = PageVersionFactory(created_by=self.user_1)
        language = page_version.content.language

        # Populate page
        placeholder = PlaceholderFactory(source=page_version.content)
        poll1_version = PollVersionFactory(created_by=self.user_2, content__language=language)
        PollPluginFactory(placeholder=placeholder, poll=poll1_version.content.poll)

        self.collection.add_version(page_version)
        self.collection.add_version(poll1_version)

        self.assertEqual(ModerationRequest.objects.all().count(), 2)
