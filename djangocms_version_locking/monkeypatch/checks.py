from cms.models import fields

from djangocms_version_locking.helpers import placeholder_content_is_unlocked


fields.PlaceholderRelationField.default_checks += [placeholder_content_is_unlocked]
