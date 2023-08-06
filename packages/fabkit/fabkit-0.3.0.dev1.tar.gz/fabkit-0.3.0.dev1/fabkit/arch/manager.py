from shlex import quote

from fabric.context_managers import settings, hide

from fabkit.util import run_or_sudo, run_with_cmd_sudo


class PacmanManager:
    def upgrade_all(self, noconfirm=True, options=None):
        args = ['-Su']

        if noconfirm:
            args.append('--noconfirm')

        options = options or []
        args.extend(options)
        self._run_manager(args, None)

    def is_installed(self, pkg):
        with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
            res = self._run_manager(['-Q'], pkg, use_sudo=False)
            return res.succeeded

    def install(self, pkg, update_index=False, noconfirm=True, needed=True, options=None):
        if update_index:
            self.update_index()

        args = ['-S']

        if noconfirm:
            args.append('--noconfirm')
        if needed:
            args.append('--needed')
        options = options or []
        args.extend(options)

        self._run_manager(args, pkg)

    def uninstall(self, pkg, noconfirm=True, options=None):
        args = ['-R']

        if noconfirm:
            args.append('--noconfirm')
        options = options or []
        args.extend(options)

        self._run_manager(args, pkg)

    def update(self, pkg, update_index=False, noconfirm=True, needed=True, options=None):
        self.install(pkg, update_index, noconfirm, needed, options)

    def update_index(self):
        self._run_manager(['-Sy'], None)

    def _run_manager(self, options, pkg, use_sudo=True):
        options = ' '.join(options)

        if pkg is None:
            pkg = ''
        elif isinstance(pkg, str) and len(pkg) > 0:
            pkg = quote(pkg)
        elif isinstance(pkg, (list, tuple)):
            pkg = ' '.join(map(quote, pkg))

        return self._execute(f'{options} {pkg}', use_sudo)

    def _execute(self, cmd, use_sudo):
        return run_or_sudo(f'pacman {cmd}', use_sudo)


class AurmanManager(PacmanManager):
    def _execute(self, cmd, use_sudo):
        return run_with_cmd_sudo(f'aurman {cmd}')

    def install(self, pkg, update_index=False, noconfirm=True, needed=True, options=None):
        options = options or []
        if noconfirm:
            options.append('--noedit')

        super().install(pkg, update_index, noconfirm, needed, options)

