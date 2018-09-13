HELPER_SETTINGS = {
    'TIME_ZONE': 'Europe/London',
    'TOP_INSTALLED_APPS': [
        'djangocms_version_locking',
    ],
    'INSTALLED_APPS': [
        'djangocms_text_ckeditor',
        'djangocms_versioning',
    ],
    'MIGRATION_MODULES': {
        'auth': None,
        'cms': None,
        'menus': None,
        'djangocms_versioning': None,
        'djangocms_version_locking': None,
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
}


def run():
    from djangocms_helper import runner
    runner.cms('djangocms_version_locking', extra_args=[])


if __name__ == "__main__":
    run()
