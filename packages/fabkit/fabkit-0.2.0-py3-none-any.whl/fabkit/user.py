from crypt import crypt
from datetime import date
from secrets import choice
from string import ascii_letters, digits
from typing import List
from shlex import quote

from fabric.context_managers import settings, hide
from fabric.operations import run, sudo


def exists(name):
    with settings(hide('running', 'stdout', 'warnings'), warn_only=True):
        return run('getent passwd %(name)s' % locals()).succeeded


def create(name: str, full_name: str = None, home_dir: str = None, create_home: bool = None, expire_date: date = None,
           inactive: int = None, group: str = None, other_groups: List[str] = None, system_account: bool = False,
           shell: str = None, password: str = None):
    """
    Create user account via 'useradd' cmd

    :param str name: account name
    :param str full_name: user's full name (comment)
    :param str home_dir: path to user's home dir
    :param bool create_home: forces to create (or not) user's home dir. If not set
                             then system default value will be used
    :param datetime expire_date: the date on which the user account will be disabled
    :param int inactive: the number of days after a password expires until the account is permanently disabled.
                         A value of 0 disables the account as soon as the password has expired,
                         and a value of -1 disables the feature.
    :param str group: The group name or number of the user's initial login group. The group name must exist.
                      A group number must refer to an already existing group.
    :param list[str] other_groups: A list of supplementary groups which the user is also a member of.
                                   Each group is separated from the next by a comma, with no intervening whitespace.
    :param bool system_account: Create a system account.
    :param str shell: The name of the user's login shell.
    :param str password: user's password
    """
    options = []
    if full_name:
        options.append(f'-c {quote(full_name)}')
    if home_dir:
        options.append(f'-d {quote(home_dir)}')
    if create_home is not None:
        if create_home:
            options.append('-m')
        else:
            options.append('-M')
    if expire_date:
        expiration_date = expire_date.strftime("%Y-%m-%d")
        options.append(f'-e {expiration_date}')
    if inactive is not None:
        options.append(f'-f {int(inactive)}')
    if group:
        group = str(group)
        options.append(f'-g {group}')
    if other_groups:
        groups = ','.join(map(str, other_groups))
        options.append(f'-G {groups}')
    if system_account:
        options.append('-r')
    if shell:
        options.append(f'-s {quote(shell)}')
    if password:
        encrypted_password = _encrypt_password(password)
        options.append(f'-p {quote(encrypted_password)}')

    username = quote(name)
    args = ' '.join(options)
    sudo(f'useradd {args} {username}')


_SALT_CHARS = ascii_letters + digits + "./"


def _encrypt_password(password):
    salt = choice(_SALT_CHARS) + choice(_SALT_CHARS)
    return crypt(password, salt)



