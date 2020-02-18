from setuptools import find_packages, setup

import djangocms_version_locking


INSTALL_REQUIREMENTS = [
    'Django>=1.11,<2.1',
    'django-cms',
]

TEST_REQUIREMENTS = [
    "djangocms_helper",
    "djangocms_versioning",
    "factory_boy",
    "djangocms-text-ckeditor",
]


setup(
    name='djangocms-version-locking',
    packages=find_packages(),
    include_package_data=True,
    version=djangocms_version_locking.__version__,
    description=djangocms_version_locking.__doc__,
    long_description=open('README.rst').read(),
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
    install_requires=INSTALL_REQUIREMENTS,
    author='Fidelity International',
    test_suite='test_settings.run',
    url='http://github.com/divio/djangocms-version-locking',
    license='BSD',
    zip_safe=False,
    tests_require=TEST_REQUIREMENTS,
    dependency_links=[
        "http://github.com/divio/django-cms/tarball/release/4.0.x#egg=django-cms-4.0.0",
        "http://github.com/divio/djangocms-versioning/tarball/master#egg=djangocms-versioning-0.0.23",
        # required because it is required in tests in djangocms-versioning
        "https://github.com/divio/djangocms-text-ckeditor/tarball/support/4.0.x#egg=djangocms-text-ckeditor-4.0.x",
    ]
)
