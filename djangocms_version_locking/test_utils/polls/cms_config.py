from cms.app_base import CMSAppConfig

from djangocms_versioning.datastructures import VersionableItem, default_copy

from .models import PollContent


def get_poll_additional_changelist_action(obj):
    return f"Custom poll action {obj.pk}"


def get_poll_additional_changelist_field(obj):
    return f"Custom poll link {obj.pk}"


class PollsCMSConfig(CMSAppConfig):
    # Versioning enabled
    djangocms_versioning_enabled = True
    versioning = [
        VersionableItem(
            content_model=PollContent,
            grouper_field_name='poll',
            copy_function=default_copy,
        ),
    ]
    # Version locking enabled
    djangocms_version_locking_enabled = True
    version_lock_models = [PollContent, ]
    # Moderation enabled
    djangocms_moderation_enabled = True
    moderated_models = (PollContent,)
    moderation_request_changelist_actions = [get_poll_additional_changelist_action]
    moderation_request_changelist_fields = [get_poll_additional_changelist_field]
