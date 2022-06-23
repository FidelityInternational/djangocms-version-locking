from setuptools import find_packages, setup

import djangocms_version_locking


INSTALL_REQUIREMENTS = [
    'Django>=2.2,<4.0',
    'django-cms',
]

TEST_REQUIREMENTS = [
    "djangocms_alias",
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
    tests_require=TEST_REQUIREMENTS,
    author='Fidelity International',
    test_suite='test_settings.run',
    url='http://github.com/divio/djangocms-version-locking',
    license='BSD',
    dependency_links=[
        "http://github.com/django-cms/djangocms-alias/tarball/master#egg=djangocms-alias",
    ]
)
