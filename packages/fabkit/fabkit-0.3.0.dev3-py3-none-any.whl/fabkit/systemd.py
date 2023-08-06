from shlex import quote

from fabric.context_managers import settings, hide
from fabric.operations import sudo


class SystemdService:
    def __init__(self, service):
        self._name = quote(service)

    def enable(self):
        """
        Enable a service.
        """
        self._action('enable')

    def disable(self):
        """
        Disable a service.
        """
        self._action('disable')

    def is_running(self):
        """
        Check if a service is running.
        """
        with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
            return self._action('status').succeeded

    def start(self):
        """
        Start a service.
        """
        self._action('start')

    def stop(self):
        """
        Stop a service.
        """
        self._action('stop')

    def restart(self):
        """
        Restart a service.
        """
        self._action('restart')

    def reload(self):
        """
        Reload a service.
        """
        self._action('reload')

    @staticmethod
    def daemon_reload():
        sudo('systemctl daemon-reload')

    def _action(self, action):
        return sudo(f'systemctl {action} {self._name}')
