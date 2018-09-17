from .helpers import content_is_unlocked


def placeholder_content_is_unlocked(placeholder, user):
    content = placeholder.source
    return content_is_unlocked(content, user)
