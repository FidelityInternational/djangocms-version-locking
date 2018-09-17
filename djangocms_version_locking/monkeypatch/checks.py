from cms.models import fields

from ..check import content_is_unlocked


fields.PlaceholderRelationField.default_checks += [content_is_unlocked]
