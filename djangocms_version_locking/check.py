from django.contrib.contenttypes.models import ContentType

from .models import VersionLock


def content_is_not_locked(placeholder, user):
    """Pass the check if lock doesn't exist or
    object is locked to provided user.
    """
    content = placeholder.source
    try:
        lock = VersionLock.objects.get(
            version__content_type=ContentType.objects.get_for_model(content),
            version__object_id=content.pk,
        )
    except VersionLock.DoesNotExist:
        return True
    return lock.created_by == user
