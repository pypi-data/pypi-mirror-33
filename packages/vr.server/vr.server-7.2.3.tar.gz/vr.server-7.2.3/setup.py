#!/usr/bin/env python

# Project skeleton maintained at https://github.com/jaraco/skeleton

import io

import setuptools

with io.open('README.rst', encoding='utf-8') as readme:
    long_description = readme.read()

name = 'vr.server'
description = 'Velociraptor\'s Django and Celery components.'
nspkg_technique = 'managed'
"""
Does this package use "native" namespace packages or
pkg_resources "managed" namespace packages?
"""

params = dict(
    name=name,
    use_scm_version=True,
    author="Brent Tubbs",
    author_email="btubbs@gmail.com",
    description=description or name,
    long_description=long_description,
    url="https://github.com/yougov/" + name,
    packages=setuptools.find_packages(),
    include_package_data=True,
    namespace_packages=(
        name.split('.')[:-1] if nspkg_technique == 'managed'
        else []
    ),
    python_requires='>=2.7',
    install_requires=[
        'celery-schedulers==0.0.2',
        'diff-match-patch==20121119',
        'Django>=1.8,<1.9',
        'django-celery>=3.1.17,<3.2',
        'django-extensions==1.5.9',
        'django-picklefield==0.2.0',
        'django-redis-cache==0.9.5',
        'django-reversion==1.9.3',
        'django-tastypie==0.12.2',
        'Fabric3',
        'gevent>=1.1rc1,<2',
        'psycogreen',
        'gunicorn==0.17.2',
        'psycopg2>=2.4.4',
        'pymongo>=2.5.2,<4',
        'redis>=2.6.2,<3',
        'requests>=2.11.1',
        'setproctitle',
        'sseclient==0.0.11',
        'six>=1.4',
        'vr.events>=1.2.1',
        'vr.common>=4.9.3',
        'vr.builder>=1.3',
        'vr.imager>=1.3',
        'django-yamlfield',
        'backports.functools_lru_cache',
        # Celery 4 removes support for e-mail
        # https://github.com/celery/celery/blob/master/docs/whatsnew-4.0.rst#removed-features
        'celery<4dev',
        'jaraco.functools',
        'backports.datetime_timestamp',
        'tempora',
    ],
    extras_require={
        'testing': [
            # upstream
            'pytest>=2.8',
            'pytest-sugar>=0.9.1',
            'collective.checkdocs',
            'pytest-flake8',

            # local
            'backports.unittest_mock',
            'jaraco.mongodb >= 3.11',
            'python-dateutil >= 2.4',
            'jaraco.postgres >= 1.3.1',
            'path.py >= 10.0',
        ],
        'docs': [
            # upstream
            'sphinx',
            'jaraco.packaging>=3.2',
            'rst.linker>=1.9',

            # local
        ],
        ':python_version=="2.7"': [
            'mercurial>=3.8',
        ],
    },
    setup_requires=[
        'setuptools_scm>=1.15.0',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        'console_scripts': [
            'vr_worker = vr.server.commands:start_celery',
            'vr_beat = vr.server.commands:start_celerybeat',
            'vr_migrate = vr.server.commands:run_migrations',
        ],
    },
)
if __name__ == '__main__':
    setuptools.setup(**params)
