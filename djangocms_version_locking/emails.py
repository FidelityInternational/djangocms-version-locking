from django.utils.translation import ugettext_lazy as _

from cms.utils import get_current_site

from .helpers import send_email


def notify_version_author_version_unlocked(version, unlocking_user):

    # If the unlocking user is the current author, don't send an email
    if version.created_by == unlocking_user:
        return

    site = get_current_site()
    recipients = [version.created_by]
    subject = "[Django CMS] ({site_name}) {page_title} - {description}".format(
        site_name=site.name,
        page_title=version.content,
        description=_("Unlocked"),
    )

    template_context = {
        'author_name': version.created_by,
        'page_url': '',
        'by_user': unlocking_user,
    }

    status = send_email(
        recipients=recipients,
        subject=subject,
        template='unlock-notification.txt',
        template_context=template_context,
    )

    return status
