from fabric.context_managers import settings, hide
from fabric.operations import run


def cpu_nb():
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        output = run('nproc --all')
    return int(output)
