from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from cms.utils import get_current_site

from .helpers import send_email
from .utils import get_absolute_url


def notify_version_author_version_unlocked(version, unlocking_user):
    # If the unlocking user is the current author, don't send a notification email
    if version.created_by == unlocking_user:
        return

    site = get_current_site()
    recipients = [version.created_by.email]
    subject = "[Django CMS] ({site_name}) {page_title} - {description}".format(
        site_name=site.name,
        page_title=version.content,
        description=_("Unlocked"),
    )
    version_url = reverse(
        'admin:cms_placeholder_render_object_preview',
        args=(version.content_type_id, version.object_id),
    )
    version_url = get_absolute_url(version_url)

    # Prepare and send the email
    template_context = {
        'author_name': version.created_by,
        'version_link': version_url,
        'by_user': unlocking_user,
    }
    status = send_email(
        recipients=recipients,
        subject=subject,
        template='unlock-notification.txt',
        template_context=template_context,
    )
    return status
