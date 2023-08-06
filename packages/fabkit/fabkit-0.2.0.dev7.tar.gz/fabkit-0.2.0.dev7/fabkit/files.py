from shlex import quote
from fabkit.util import run_or_sudo
from fabric.operations import settings, hide


def is_file(path, use_sudo=False):
    return _test('-f', path, use_sudo)


def is_dir(path, use_sudo: False):
    return _test('-d', path, use_sudo)


def is_link(path, use_sudo: False):
    return _test('-L', path, use_sudo)


def exists(path, use_sudo: False):
    return _test('-e', path, use_sudo)


def chown(path, user=None, group=None, use_sudo=False):
    if not user and not group:
        raise ValueError("[chown] One of user/group must be provided")
    if group:
        group = f':{group}'

    run_or_sudo(f'chown {user}{group} {quote(path)}', use_sudo)


def _test(option, path, use_sudo):
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        return run_or_sudo(f'test {option} {quote(path)}', use_sudo).succeeded
