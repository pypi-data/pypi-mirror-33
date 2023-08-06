from io import StringIO
from shlex import quote

from fabric.operations import put
from fabkit.files import chown


def add(user, hosts='ALL', runas='ALL', tag='', commands='ALL'):
    if isinstance(hosts, (list, tuple)):
        hosts = ', '.join(hosts)
    if isinstance(runas, (list, tuple)):
        runas = ', '.join(runas)

    if isinstance(commands, (list, tuple)):
        commands = ', '.join(commands)

    sudoer_entry = f'{user} {hosts}=({runas}) {tag} {commands}'
    sudoer_file = quote(f'/etc/sudoers.d/{user}')
    put(StringIO(sudoer_entry), sudoer_file, use_sudo=True)
    chown(sudoer_file, user='root', group='root', use_sudo=True)
