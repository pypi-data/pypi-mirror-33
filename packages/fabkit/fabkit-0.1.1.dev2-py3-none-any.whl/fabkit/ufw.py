from shlex import quote

from fabric.operations import sudo


def enable():
    sudo('ufw enable')


def disable():
    sudo('ufw disable')


def reload():
    sudo('ufw reload')


def default_deny():
    sudo('ufw default deny')


def allow_port(port, protocol='tcp'):
    _allow(f'{quote(port)}/{quote(protocol)}')


def allow_app(app):
    _allow(quote(app))


def allow_from(src):
    _allow(f'from {quote(src)}')


def _allow(cmd):
    sudo(f'ufw allow {cmd}')
