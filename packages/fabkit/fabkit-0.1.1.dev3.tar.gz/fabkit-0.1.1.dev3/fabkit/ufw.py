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
    if not isinstance(port, int):
        raise ValueError('[ufw] Port must be an integer')
    _allow(f'{port}/{quote(protocol)}')


def allow_app(app):
    _allow(quote(app))


def allow_from(src):
    _allow(f'from {quote(src)}')


def _allow(cmd):
    sudo(f'ufw allow {cmd}')
