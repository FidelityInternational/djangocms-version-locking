import factory
import string

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from cms.models import Placeholder

from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyText

from djangocms_moderation.models import ModerationCollection, Workflow

from ..models import Version
from .polls.models import Answer, Poll, PollContent, PollPlugin


class UserFactory(DjangoModelFactory):
    username = FuzzyText(length=12)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(
        lambda u: "%s.%s@example.com" % (u.first_name.lower(), u.last_name.lower()))

    class Meta:
        model = User


class AbstractVersionFactory(DjangoModelFactory):
    object_id = factory.SelfAttribute('content.id')
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content))
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        exclude = ['content']
        abstract = True


class PollFactory(DjangoModelFactory):
    name = FuzzyText(length=6)

    class Meta:
        model = Poll


class PollContentFactory(DjangoModelFactory):
    poll = factory.SubFactory(PollFactory)
    language = FuzzyChoice(['en', 'fr', 'it'])
    text = FuzzyText(length=24)

    class Meta:
        model = PollContent


class PollVersionFactory(AbstractVersionFactory):
    content = factory.SubFactory(PollContentFactory)

    class Meta:
        model = Version


class PollContentWithVersionFactory(PollContentFactory):

    @factory.post_generation
    def version(self, create, extracted, **kwargs):
        # NOTE: Use this method as below to define version attributes:
        # PollContentWithVersionFactory(version__label='label1')
        if not create:
            # Simple build, do nothing.
            return
        PollVersionFactory(content=self, **kwargs)


class AnswerFactory(DjangoModelFactory):
    poll_content = factory.SubFactory(PollContentFactory)
    text = factory.LazyAttributeSequence(
        lambda o, n: 'Poll %s - Answer %d' % (o.poll_content.poll.name, n))

    class Meta:
        model = Answer


class WorkflowFactory(DjangoModelFactory):
    name = FuzzyText(length=12)

    class Meta:
        model = Workflow


class ModerationCollectionFactory(DjangoModelFactory):
    name = FuzzyText(length=12)
    author = factory.SubFactory(UserFactory)
    workflow = factory.SubFactory(WorkflowFactory)

    class Meta:
        model = ModerationCollection


class PlaceholderFactory(DjangoModelFactory):
    default_width = FuzzyInteger(0, 25)
    slot = FuzzyText(length=2, chars=string.digits)
    # NOTE: When using this factory you will probably want to set
    # the source field manually

    class Meta:
        model = Placeholder


def get_plugin_language(plugin):
    """Helper function to get the language from a plugin's relationships.
    Use this in plugin factory classes
    """
    if plugin.placeholder.source:
        return plugin.placeholder.source.language
    # NOTE: If plugin.placeholder.source is None then language will
    # also be None unless set manually


def get_plugin_position(plugin):
    """Helper function to correctly calculate the plugin position.
    Use this in plugin factory classes
    """
    offset = plugin.placeholder.get_last_plugin_position(plugin.language) or 0
    return offset + 1


class PollPluginFactory(DjangoModelFactory):
    language = factory.LazyAttribute(get_plugin_language)
    placeholder = factory.SubFactory(PlaceholderFactory)
    parent = None
    position = factory.LazyAttribute(get_plugin_position)
    plugin_type = "PollPlugin"
    poll = factory.SubFactory(PollFactory)

    class Meta:
        model = PollPlugin
