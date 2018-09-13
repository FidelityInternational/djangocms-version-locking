from cms.app_base import CMSAppConfig

from .models import PollContent


class PollsCMSConfig(CMSAppConfig):
    djangocms_version_locking_enabled = True
    version_lock_list = [PollContent,]
