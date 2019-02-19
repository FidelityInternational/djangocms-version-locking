from cms.app_base import CMSAppExtension


class VersionLockingCMSExtension(CMSAppExtension):
    def __init__(self):
        # The monkey patch is here to be sure that at module load time the Version class
        # is registered and can be overriden without requiring a strict load order
        # in the INSTALLED_APPS setting in a projects settings.py. This is why this patch
        # Isn't loaded from: VersionLockingConfig.ready
        from .monkeypatch import admin as monkeypatch_admin

    def configure_app(self, cms_config):
        pass
