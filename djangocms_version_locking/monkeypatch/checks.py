from cms.models import fields

from ..check import content_is_not_locked


fields.PlaceholderRelationField.default_checks += [content_is_not_locked]
