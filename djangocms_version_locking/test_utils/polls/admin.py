from django.contrib import admin

from djangocms_version_locking.admin import VersionLockContentAdminMixin

from .models import Answer, Poll, PollContent


@admin.register(PollContent)
class PollContentAdmin(VersionLockContentAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    pass


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    pass
