import os
import sys

import pytest
from django import setup

from vr.server.tests import dbsetup


def _path_hack():
    """
    hack the PYTHONPATH to ensure that re-entrant processes
    have access to packages loaded by pytest-runner.
    """
    os.environ['PYTHONPATH'] = os.pathsep.join(sys.path)


def pytest_configure():
    """
    Setup the django instance before to run the tests

    Starting from django 1.7 we need to let django to setup itself.
    """
    _path_hack()
    setup()
    _setup_allowed_hosts()


def _setup_allowed_hosts():
    '''Allow the hostname we use for testing.'''
    from django.conf import settings
    settings.ALLOWED_HOSTS = ['testserver']


@pytest.fixture(scope="session")
def gridfs(mongodb_instance):
    from django.conf import settings
    settings.GRIDFS_PORT = mongodb_instance.port
    settings.MONGODB_URL = mongodb_instance.get_uri() + '/velociraptor'
    patch_default_storage()


def patch_default_storage():
    """
    By the time the tests run, django has already started up
    and configured the default_storage for files, binding the
    GridFSStorage to the default host/port. But the test suite
    has gone to a lot of trouble to supply an ephemeral instance
    of MongoDB, so re-init the default storage to use that
    instance.
    """
    import django
    django.core.files.storage.default_storage.__init__()


@pytest.fixture
def postgresql(request):
    if not request.config.getoption('--use-local-db'):
        postgresql_instance = request.getfuncargvalue('postgresql_instance')
        from django.conf import settings
        port = postgresql_instance.port
        settings.DATABASES['default']['PORT'] = str(postgresql_instance.port)
    else:
        port = None
    dbsetup(port)


@pytest.fixture()
def redis():
    try:
        redis = __import__('redis')
        redis.StrictRedis(host='localhost', port=6379).echo('this')
    except Exception as exc:
        tmpl = "Unable to establish connection to redis ({exc})"
        pytest.skip(tmpl.format(**locals()))


def pytest_addoption(parser):
    parser.addoption(
        '--use-local-db', action='store_true',
        default=False,
        help="Use a local, already configured database",
    )
