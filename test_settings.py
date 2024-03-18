HELPER_SETTINGS = {
    'SECRET_KEY': 'djangocms-version-locking-test-suite',
    'TIME_ZONE': 'Europe/London',
    'INSTALLED_APPS': [
        'djangocms_text_ckeditor',
        'djangocms_versioning',
        'djangocms_version_locking',
        'djangocms_version_locking.test_utils.polls',
        'djangocms_alias',
        'djangocms_moderation',
    ],
    'MIGRATION_MODULES': {
        'auth': None,
        'cms': None,
        'menus': None,
        'djangocms_versioning': None,
        'djangocms_version_locking': None,
        'djangocms_alias': None,
        'djangocms_moderation': None,
        'djangocms_text_ckeditor': None
    },
    'CMS_PERMISSION': True,
    'LANGUAGES': (
        ('en', 'English'),
        ('de', 'German'),
        ('fr', 'French'),
        ('it', 'Italiano'),
    ),
    'CMS_LANGUAGES': {
        1: [
            {
                'code': 'en',
                'name': 'English',
                'fallbacks': ['de', 'fr']
            },
            {
                'code': 'de',
                'name': 'Deutsche',
                'fallbacks': ['en']  # FOR TESTING DO NOT ADD 'fr' HERE
            },
            {
                'code': 'fr',
                'name': 'Française',
                'fallbacks': ['en']  # FOR TESTING DO NOT ADD 'de' HERE
            },
            {
                'code': 'it',
                'name': 'Italiano',
                'fallbacks': ['fr']  # FOR TESTING, LEAVE AS ONLY 'fr'
            },
        ],
    },
    'PARLER_ENABLE_CACHING': False,
    'LANGUAGE_CODE': 'en',
    'DEFAULT_AUTO_FIELD': 'django.db.models.AutoField',
}


def run():
    from app_helper import runner
    runner.cms('djangocms_version_locking', extra_args=[])


if __name__ == "__main__":
    run()
