from cms.test_utils.testcases import CMSTestCase
from cms.utils.urlutils import add_url_parameters

from djangocms_moderation.models import ModerationRequest
from djangocms_moderation.utils import get_admin_url
from djangocms_versioning.test_utils.factories import PageVersionFactory

from djangocms_version_locking.helpers import remove_version_lock
from djangocms_version_locking.test_utils.factories import (
    ModerationCollectionFactory,
    PlaceholderFactory,
    PollPluginFactory,
    PollVersionFactory,
    UserFactory,
)


class ModerationCollectionTestCase(CMSTestCase):
    def setUp(self):
        self.language = "en"
        self.user_1 = self.get_superuser()
        self.user_2 = UserFactory()
        self.collection = ModerationCollectionFactory(author=self.user_1)
        self.page_version = PageVersionFactory(created_by=self.user_1)
        self.placeholder = PlaceholderFactory(source=self.page_version.content)
        self.poll_version = PollVersionFactory(created_by=self.user_2, content__language=self.language)

    def test_add_version_with_locked_plugins(self):
        """
        Locked plugins should not be allowed to be added to a collection
        """
        PollPluginFactory(placeholder=self.placeholder, poll=self.poll_version.content.poll)

        admin_endpoint = get_admin_url(
            name="cms_moderation_items_to_collection", language="en", args=()
        )

        url = add_url_parameters(
            admin_endpoint,
            return_to_url="http://example.com",
            version_ids=self.page_version.pk,
            collection_id=self.collection.pk,
        )

        with self.login_user_context(self.user_1):
            self.client.post(
                path=url,
                data={"collection": self.collection.pk, "versions": [self.page_version.pk]},
                follow=False,
            )

        # Match collection and versions in the DB
        stored_collection = ModerationRequest.objects.filter(collection=self.collection)

        self.assertEqual(stored_collection.count(), 1)

    def test_add_version_with_unlocked_child(self):
        """
        Only plugins that are unlocked should be added to collection
        """

        PollPluginFactory(placeholder=self.placeholder, poll=self.poll_version.content.poll)

        admin_endpoint = get_admin_url(
            name="cms_moderation_items_to_collection", language="en", args=()
        )

        url = add_url_parameters(
            admin_endpoint,
            return_to_url="http://example.com",
            version_ids=self.page_version.pk,
            collection_id=self.collection.pk,
        )

        # Unlock the poll version
        remove_version_lock(self.poll_version)

        with self.login_user_context(self.user_1):
            self.client.post(
                path=url,
                data={"collection": self.collection.pk, "versions": [self.page_version.pk]},
                follow=False,
            )

        # Match collection and versions in the DB
        stored_collection = ModerationRequest.objects.filter(collection=self.collection)

        self.assertEqual(stored_collection.count(), 2)
