from fabric.context_managers import settings
from fabric.operations import run, sudo
from fabric.state import env


def run_or_sudo(cmd, use_sudo, **kwargs):
    runner = sudo if use_sudo else run
    return runner(cmd, **kwargs)


def run_with_cmd_sudo(*args, **kwargs):
    with settings(sudo_prompt="[sudo] password for {user}: ".format(user=env.user)):
        return run(*args, **kwargs)
