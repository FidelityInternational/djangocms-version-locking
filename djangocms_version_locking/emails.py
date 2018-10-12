from django.utils.translation import ugettext_lazy as _

from cms.toolbar.utils import get_object_preview_url
from cms.utils import get_current_site

from .helpers import send_email
from .utils import get_absolute_url


def notify_version_author_version_unlocked(version, unlocking_user):
    # If the unlocking user is the current author, don't send a notification email
    if version.created_by == unlocking_user:
        return

    # If the users name is available use it, otherwise use their username
    username = unlocking_user.get_full_name()
    if username == "":
        username = unlocking_user.username


    site = get_current_site()
    recipients = [version.created_by.email]
    subject = "[Django CMS] ({site_name}) {title} - {description}".format(
        site_name=site.name,
        title=version.content,
        description=_("Unlocked"),
    )
    version_url = get_absolute_url(
        get_object_preview_url(version.content)
    )

    # Prepare and send the email
    template_context = {
        'version_link': version_url,
        'by_user': username,
    }
    status = send_email(
        recipients=recipients,
        subject=subject,
        template='unlock-notification.txt',
        template_context=template_context,
    )
    return status
