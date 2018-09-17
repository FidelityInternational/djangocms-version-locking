from cms.app_base import CMSAppConfig

from djangocms_versioning.datastructures import VersionableItem, default_copy

from .models import PollContent


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
    version_lock_models = [PollContent,]

