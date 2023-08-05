from shlex import quote

from fabric.context_managers import settings, hide

from fabkit.util import run_or_sudo, run_with_cmd_sudo


class PacmanManager:
    def upgrade_all(self, noconfirm=True):
        options = ['-Su']

        if noconfirm:
            options.append('--noconfirm')

        self._run_manager(options, None)

    def is_installed(self, pkg):
        with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
            res = self._run_manager(['-Q'], pkg, use_sudo=False)
            return res.succeeded

    def install(self, pkg, update_index=False, noconfirm=True, needed=True):
        if update_index:
            self.update_index()

        options = ['-S']

        if noconfirm:
            options.append('--noconfirm')
        if needed:
            options.append('--needed')

        self._run_manager(options, pkg)

    def uninstall(self, pkg, noconfirm=True):
        options = ['-R']

        if noconfirm:
            options.append('--noconfirm')

        self._run_manager(options, pkg)

    def update(self, pkg, noconfirm=True):
        pass

    def update_index(self):
        self._run_manager(['-Sy'], None)

    def _run_manager(self, options, pkg, use_sudo=True):
        options = ' '.join(options)
        if pkg is None:
            pkg = ''

        if isinstance(pkg, (list, tuple)):
            pkg = ' '.join(pkg)

        pkg = quote(pkg)
        return self._execute(f'{options} {pkg}', use_sudo)

    def _execute(self, cmd, use_sudo):
        return run_or_sudo(f'pacman {cmd}', use_sudo)


class AurmanManager(PacmanManager):
    def _execute(self, cmd, use_sudo):
        return run_with_cmd_sudo(f'aurman {cmd}')
