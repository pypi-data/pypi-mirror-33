"""
Utilities for running commands and reading/writing files on remote hosts over
SSH.
"""

from __future__ import print_function

import traceback
import posixpath
import json
import os
import re
import datetime
import contextlib
import platform

import pkg_resources
import yaml
from fabric.api import (
    sudo as sudo_, get, put, task, env, settings as fab_settings, hide, run)
from fabric.contrib import files
from fabric.context_managers import cd, shell_env

from vr.common.models import ProcData, ProcError
from vr.common.paths import (
    BUILDS_ROOT, IMAGES_ROOT, PROCS_ROOT, get_proc_path,
    get_container_name, get_container_path)
from vr.common.utils import randchars
from vr.builder.main import BuildData

from vr.server.models import Host


# How long ago must an image/build be last accessed before being
# removed from host?
MAX_IMAGE_AGE = datetime.timedelta(days=7)
MAX_BUILD_AGE = datetime.timedelta(days=7)

# Supervisorctl may take a long time and even hang.
# Specify a timeout before giving up.
SUPERVISORCTL_TIMEOUT = 60


def get_template(name):
    return pkg_resources.resource_filename('vr.common', 'templates/' + name)


def print_host(msg, *args, **kwargs):
    """Prepend hostname to output message, if possible."""
    try:
        header = '{}: '.format(env.host_string)
    except Exception:
        header = ''
    print(header + msg, *args, **kwargs)


class Error(Exception):
    """
    An exception representing a remote command error.
    """
    def __init__(self, out):
        self.out = out
        super(Error, self).__init__(out)

    @property
    def title(self):
        return ("Command failed with exit code {self.return_code}: "
                "{self.command}".format(self=self))

    def __getattr__(self, attr):
        return getattr(self.out, attr)

    @classmethod
    def handle(cls, out):
        if out.failed:
            raise cls(out)
        return out


def sudo(*args, **kwargs):
    """
    Wrap fabric's sudo to trap errors and raise them.
    """
    kwargs.setdefault('warn_only', True)
    return Error.handle(sudo_(*args, **kwargs))


def supervisorctl(cmd):
    with fab_settings(command_timeout=SUPERVISORCTL_TIMEOUT):
        return sudo('supervisorctl ' + cmd)


@task
def deploy_proc(proc_yaml_path):
    """
    Given a path to a proc.yaml file, get that proc set up on the remote host.
    The runner's "setup" command will do most of the work.
    """
    settings = load_proc_data(proc_yaml_path)
    proc_path = get_proc_path(settings)
    sudo('mkdir -p ' + proc_path)

    remote_proc_yaml = posixpath.join(proc_path, 'proc.yaml')
    put(proc_yaml_path, remote_proc_yaml, use_sudo=True)

    sudo(get_runner(settings) + ' setup ' + remote_proc_yaml)
    write_proc_conf(settings)
    supervisorctl('reread')
    supervisorctl('add ' + get_container_name(settings))


def write_proc_conf(settings):
    proc_path = get_proc_path(settings)
    proc_conf_vars = {
        'proc_yaml_path': posixpath.join(proc_path, 'proc.yaml'),
        'container_name': get_container_name(settings),
        'container_path': get_container_path(settings),
        'log': posixpath.join(proc_path, 'log'),
        'runner': get_runner(settings),
        'user': 'root',
    }
    proc_conf_tmpl = get_template('proc.conf')
    files.upload_template(
        proc_conf_tmpl,
        posixpath.join(proc_path, 'proc.conf'),
        proc_conf_vars,
        use_sudo=True)


@task
def run_uptests(
        hostname, proc_name, user='nobody', ignore_missing_procs=False):
    try:
        host = Host.objects.get(name=hostname)

        try:
            proc = host.get_proc(proc_name)
        except ProcError:
            if ignore_missing_procs:
                print_host('Missing proc {}'.format(proc_name))
                return []
            raise

        settings = proc.settings
        if settings is None:
            print_host(
                '{0.name} (pid {0.pid}) running on {0.hostname} '
                'is not a VR process.  Skipping...'.format(proc))
            return []

        proc_path = get_proc_path(settings)

        new_container_path = posixpath.join(proc_path, 'rootfs')
        if files.exists(new_container_path, use_sudo=True):
            tests_path = posixpath.join(new_container_path, 'app/uptests',
                                        settings.proc_name)
        else:
            build_path = get_build_path(settings)
            tests_path = posixpath.join(
                build_path, 'uptests', settings.proc_name)

        if not files.exists(tests_path, use_sudo=True):
            return []

        # Containers set up by new-style 'runners' will be in a 'rootfs'
        # subpath under the proc_path.  Old style containers are right in
        # the proc_path.  We have to launch the uptester slightly
        # differently
        if files.exists(new_container_path, use_sudo=True):
            proc_yaml_path = posixpath.join(proc_path, 'proc.yaml')
            cmd = get_runner(settings) + ' uptest ' + proc_yaml_path
        else:
            cmd = legacy_uptests_command(
                proc_path, settings.proc_name, env.host_string,
                settings.port, user)

        result = sudo(cmd)
        # Though the uptester emits JSON to stdout, it's possible for the
        # container or env var setup to emit some other output before the
        # uptester even runs.  Stuff like this:

        # 'bash: /app/env.sh: No such file or directory'

        # Split that off and prepend it as an extra first uptest result.
        # Since results should be a JSON list, look for any characters
        # preceding the first square bracket.

        m = re.match(r'(?P<prefix>[^\[]*)(?P<json>.*)', result, re.S)

        # If the regular expression doesn't even match, return the raw
        # string.
        if m is None:
            return [{
                'Passed': False,
                'Name': 'uptester',
                'Output': result,
            }]

        parts = m.groupdict()
        try:
            parsed = json.loads(parts['json'])
            if parts['prefix']:
                parsed.insert(0, {
                    'Passed': False,
                    'Name': 'uptester',
                    'Output': parts['prefix']
                })
            return parsed
        except ValueError:
            # If we still fail parsing the json, return a dict of our own
            # with all the output inside.
            return [{
                'Passed': False,
                'Name': 'uptester',
                'Output': result
            }]

    except Error as error:
        # An error occurred in the command invocation, including if an
        # incorrect password is supplied and abort_on_prompts is True.
        return [{
            'Name': None,
            'Output': repr(error.out),
            'Passed': False,
        }]

    except Exception:
        # Catch any other exception raised
        # during the uptests and pass it back in the same format as other test
        # results.
        return [{
            'Name': None,
            'Output': traceback.format_exc(),
            'Passed': False,
        }]


def legacy_uptests_command(proc_path, proc, host, port, user):
    """
    Build the command string for uptesting the given proc inside its lxc
    container.
    """
    cmd = "/uptester %(folder)s %(host)s %(port)s" % {
        'folder': posixpath.join('/app/uptests', proc),
        'host': host,
        'port': port,
    }
    tmpl = (
        """exec lxc-start --name %(container_name)s -f %(lxc_config_path)s """
        """-- su --preserve-environment --shell /bin/bash """
        """-c "cd /app;source /env.sh; exec %(cmd)s" %(user)s"""
    )
    return tmpl % {
        'cmd': cmd,
        'user': user,
        'container_name': posixpath.basename(proc_path) + '-uptest',
        'lxc_config_path': posixpath.join(proc_path, 'proc.lxc'),
    }


@task
def delete_proc(hostname, proc):
    if not proc:
        raise SystemExit("You must supply a proc name")

    # Get proc settings before removing the proc from supervisor
    try:
        settings = _get_proc_settings(hostname, proc)
    except ProcError:
        # Maybe someone deleted it manually, already
        print_host(
            'delete_proc: Failed getting psettings for {}'.format(proc))
        settings = None

    # Get the pid of the proc we are trying to stop
    pid = supervisorctl('pid %s' % proc)

    # Even if we couldn't get the settings, go ahead and try to stop it
    print_host('delete_proc: Stopping proc {} pid={}'.format(proc, pid))
    supervisorctl('stop %s' % proc)

    # Kill orphans, just in case we created some
    kill_orphans()

    print_host('delete_proc: Removing proc {} in supervisorctl'.format(proc))
    supervisorctl('remove %s' % proc)

    # Try to teardown
    teardown(proc, settings)

    print_host('delete_proc: Done.')


def _get_proc_settings(hostname, proc):
    host = Host.objects.get(name=hostname)
    print_host('delete_proc: Getting settings')
    settings = host.get_proc(proc).settings
    return settings


def teardown(proc, settings):
    '''Teardown proc by removing any files in /app/procs/<procname>.

    Use runner as defined in `settings` or `vrun` if settings is None.
    '''

    # Make sure we have a proc to process
    if not proc:
        return

    proc_dir = posixpath.join(PROCS_ROOT, proc)
    proc_yaml_path = posixpath.join(proc_dir, 'proc.yaml')

    if files.exists(proc_yaml_path, use_sudo=True):
        runner = get_runner(settings) if settings else 'vrun'
        print_host(
            'delete_proc: Tearing down proc {} with runner {}'.format(
                proc, runner))
        sudo(runner + ' teardown ' + proc_yaml_path)
        print_host('teardown: Tearing down proc {} done'.format(proc))
    else:
        print_host('teardown: Missing proc.yaml: {}'.format(proc_yaml_path))
        return

    if files.exists(proc_dir, use_sudo=True):
        print_host('teardown: Removing proc dir: {}'.format(proc_dir))
        sudo('rm -rf %s' % proc_dir)
    else:
        print_host('teardown: Missing proc dir: {}'.format(proc_dir))


def proc_to_build(proc):
    parts = proc.split('-')
    return '-'.join(parts[:2])


def get_build_procs(build):
    """
    Given a build name like "some_app-v3", return a list of all the folders in
    /apps/procs that are using that build.
    """
    allprocs = get_procs()
    # Rely on the fact that proc names start with app-version, same as a build.

    return [p for p in allprocs if proc_to_build(p) == build]


@task
def delete_build(build_path, cascade=False):
    print_host('Cleaning build {}'.format(build_path))

    assert build_path.startswith(BUILDS_ROOT), 'Invalid build_path: {}'.format(
        build_path)
    assert files.exists(build_path), 'Build tarball {} does not exist'.format(
        build_path)

    tarball = os.path.basename(build_path)
    build_name = '-'.join(tarball.split('-')[:2])
    build_procs = get_build_procs(build_name)
    if build_procs:
        if not cascade:
            raise SystemExit("NOT DELETING %s. Build is currently in use, "
                             "and cascade=False" % build_name)
        else:
            for proc in build_procs:
                delete_proc(env.host_string, proc)
    sudo('rm -f {}'.format(build_path))


def _get_builds_in_use():
    procs = get_procs()
    builds_in_use = set([proc_to_build(p) for p in procs])
    return builds_in_use


def clean_builds_folders():
    """
    Check in builds_root for builds not being used by releases.
    """

    print_host('Cleaning builds')
    if files.exists(BUILDS_ROOT, use_sudo=True):
        builds_in_use = _get_builds_in_use()
        all_build_tarballs = set(get_builds())

        unused_build_tarballs = set()
        for tarball in all_build_tarballs:
            b = proc_to_build(tarball)
            build_path = os.path.join(BUILDS_ROOT, tarball)
            obsolete = _is_build_obsolete(build_path)
            if b not in builds_in_use and obsolete:
                unused_build_tarballs.add(build_path)

        for build in unused_build_tarballs:
            delete_build(build)


def _is_file_obsolete(fpath, maxage):
    stat_args = '-f "%a"' if platform.system() == 'Darwin' else '-c "%X"'
    atime_ts = int(sudo('stat {stat_args} {fpath}'.format(**locals())))
    atime = datetime.datetime.fromtimestamp(atime_ts)
    age = datetime.datetime.now() - atime
    return age > maxage


def _is_build_obsolete(build_path):
    return _is_file_obsolete(build_path, MAX_BUILD_AGE)


def _is_image_obsolete(img_path):
    return _is_file_obsolete(img_path, MAX_IMAGE_AGE)


def _rm_image(img_path):
    assert img_path, 'Empty img_path'
    assert img_path.startswith(IMAGES_ROOT), 'Invalid img_path {}'.format(
        img_path)
    print_host('Removing image {}'.format(img_path))
    # Be careful!
    sudo('rm -rf {}'.format(img_path))


def clean_images_folders():
    """
    Check in images_root for images not being used by releases.
    """

    print_host('Cleaning images')
    try:
        if not files.exists(IMAGES_ROOT, use_sudo=True):
            # Nothing to do
            return

        all_images = set(get_images())
        images_in_use = set()
        for proc_yaml in get_installed_proc_yamls():
            images_in_use.add(proc_yaml['image_name'])

        # Set of unused images (dirnames wrt IMAGES_ROOT)
        unused_images = all_images.difference(images_in_use)
        if not unused_images:
            return

        print_host('Found {} unused images: {}'.format(
            len(unused_images), unused_images))

        # Get the ones that have not been used for a while
        obsolete_image_paths = set()
        for img in unused_images:
            img_path = os.path.join(IMAGES_ROOT, img)
            if (files.exists(img_path, use_sudo=True) and
                    _is_image_obsolete(img_path)):
                obsolete_image_paths.add(img_path)

        if not obsolete_image_paths:
            return

        print_host('Found {} obsolete image paths: {}'.format(
            len(obsolete_image_paths), obsolete_image_paths))
        for img_path in obsolete_image_paths:
            _rm_image(img_path)

    except Exception:
        print_host(
            'Failed to remove images: {}'.format(traceback.format_exc()))


def _get_procnames_from_output(output):
    procnames = set()
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        procname = line.split()[0]
        procnames.add(procname)
    return procnames


def get_supervised_procnames():
    """Return a list of procnames under supervisor."""
    with fab_settings(hide('stdout')):
        output = supervisorctl('status')
    return _get_procnames_from_output(output)


def get_installed_procnames():
    """Get a list of procs currently on the file system."""
    return set(get_procs())


def get_installed_proc_yamls():
    """Parse and return all installed proc.yaml data."""
    proc_yamls = []
    for proc in get_installed_procnames():
        proc_yaml = os.path.join(PROCS_ROOT, proc, 'proc.yaml')
        with fab_settings(hide('stdout')):
            output = run('cat {}'.format(proc_yaml))
        data = yaml.load(output)
        proc_yamls.append(data)
    return proc_yamls


def get_old_procnames():
    """Get a list of procnames that are on the filesystem, but unknown
    to supervisor."""
    s_procnames = get_supervised_procnames()
    i_procnames = get_installed_procnames()
    return i_procnames - s_procnames


def teardown_old_procs():
    """
    Teardown old procs. Usually, old procs are removed during the
    swarm phase and replaced with the new proc. But if the swarm
    failed and did not cleanup properly, old procs can remain,
    lingering in the file system. This will cause issues if the host
    is rebooted, because supervisord will start the old procs up again
    as soon as the host comes back up.

    See https://bitbucket.org/yougov/velociraptor/issues/194.
    """

    # hostname = env.host_string
    for procname in get_old_procnames():
        print_host('teardown_old_procs: Tearing down {}'.format(procname))

        # Proc settings are always going to be unknown, because they
        # come from supervisor and this proc is "old" exactly because
        # it's unknown by supervisor.
        settings = None

        # try:
        #     settings = _get_proc_settings(hostname, procname)
        # except ProcError:
        #     print_host(
        #         'teardown_old_procs: '
        #         'Failed getting psettings for {}'.format(
        #             procname))
        #     settings = None

        teardown(procname, settings)


def get_orphans():
    with fab_settings(hide('warnings', 'stdout')):
        output = run('ps --ppid 1 -o pid,user,command', warn_only=True)
        # PID COMMAND
        # 310 upstart-udev-bridge --daemon
        # 312 /sbin/udevd --daemon
        # 596 upstart-socket-bridge --daemon

    def get_children(pid):
        with fab_settings(hide('warnings', 'stdout')):
            output = run('ps --ppid {} -o command'.format(pid), warn_only=True)
        return output.splitlines()[1:]

    orphans = set()
    for line in output.splitlines()[1:]:
        tokens = line.split()
        pid = int(tokens[0])
        user = tokens[1]
        command = ' '.join(tokens[2:]).strip()

        is_vr_command = user == 'nobody' and (
            '/app/.heroku/' in command or
            command.startswith('sudo -u nobody') or
            command.startswith('su --preserve-environment') or
            command.startswith('python'))

        if is_vr_command:
            cmds = [command] + get_children(pid)
            orphans.add((int(pid), tuple(cmds)))

    return orphans


def kill_orphans():
    """
    Delete orphans procs left behind by LXC crashes leaving orphans behind.

    See https://bitbucket.org/yougov/velociraptor/issues/195.
    """
    for pid, cmds in get_orphans():
        print_host(
            'kill_orphans: Killing pid={} and children={}'.format(pid, cmds))
        sudo('kill -9 {}'.format(pid))


@task
def get_procs():
    """
    Return the names of all the procs on the host.
    """
    procs = []
    if files.exists(PROCS_ROOT):
        # Valid procs are the ones which have a proc.yaml
        # E.g. PROCS_ROOT also contains procs that are being built,
        # which should be excluded.
        glob = os.path.join(PROCS_ROOT, '*', 'proc.yaml')
        try:
            proc_yamls = sudo('ls -1 ' + glob)
        except Error:
            print_host('No procs found')
            return procs

        procs = []
        for line in proc_yamls.splitlines():
            dirname = os.path.dirname(line.strip())[len(PROCS_ROOT) + 1:]
            dirname = dirname.strip()
            if dirname:
                procs.append(dirname)

    # filter out any .hold files
    return [p for p in procs if not p.endswith('.hold')]


@task
def get_builds():
    """
    Return the names of all the builds on the host.
    """
    return sudo('ls -1 %s' % BUILDS_ROOT).split()


@task
def get_images():
    """
    Return the names of all the images on the host.
    """
    return sudo('ls -1 %s' % IMAGES_ROOT).split()


@contextlib.contextmanager
def temp_dir():
    """
    Yield a temporary directory on a remote host as the current dir.
    """
    target = '/tmp/' + randchars()
    sudo('mkdir -p ' + target)
    with cd(target):
        try:
            yield target
        finally:
            sudo('rm -rf ' + target)


@task
def build_app(build_yaml_path):
    """
    Given the path to a build.yaml file with everything you need to make a
    build, copy it to the remote host and run the vbuild tool on it.  Then copy
    the resulting build.tar.gz and build_result.yaml back up here.
    """
    with temp_dir():
        try:
            put(build_yaml_path, 'build_job.yaml', use_sudo=True)
            with shell_env(LANG='C.UTF-8'):
                sudo('vbuild build build_job.yaml', capture_buffer_size=1024)
            # relies on the build being named build.tar.gz and the
            # manifest being named build_result.yaml.
            get('build_result.yaml', 'build_result.yaml')
            with open('build_result.yaml', 'rb') as f:
                BuildData(yaml.safe_load(f))
            get('build.tar.gz', 'build.tar.gz')
        finally:
            logfiles = ['compile.log', 'lxcdebug.log']
            for logfile in logfiles:
                try:
                    # try to get compile.log even if build fails.
                    with fab_settings(warn_only=True):
                        if files.exists(logfile):
                            get(logfile, logfile)
                        else:
                            print_host(
                                'in remote, logfile, not exist', logfile)
                except Exception:
                    print_host(
                        "Could not retrieve", logfile)


@task
def build_image(image_yaml_path):
    """
    Given the path to an image.yaml file with everything you need for 'vimage'
    to make a build, copy it to the remote host and run the vimage tool on it.
    Then copy the resulting image and compile log up here.
    """
    with open(image_yaml_path) as f:
        image_data = yaml.safe_load(f)
    with temp_dir():
        try:
            put(image_yaml_path, 'image_job.yaml', use_sudo=True)
            sudo('vimage build image_job.yaml', capture_buffer_size=1024)
            fname = '%s.tar.gz' % image_data['new_image_name']
            get(fname, fname)
        finally:
            logfile = '%(new_image_name)s.log' % image_data
            try:
                # try to get .log even if build fails.
                with fab_settings(warn_only=True):
                    get(logfile, logfile)
            except Exception:
                print_host("Could not retrieve", logfile)


def load_proc_data(proc_yaml_path):
    with open(proc_yaml_path, 'rb') as f:
        return ProcData(yaml.safe_load(f))


def get_build_path(settings):
    build_name = '{0.app_name}-{0.version}-{0.image_name}'.format(settings)
    return posixpath.join(BUILDS_ROOT, build_name)


def get_runner(settings):
    """
    Return the appropriate VR runner command to use with the given settings.
    """
    return 'vrun' if settings.image_url is not None else 'vrun_precise'
