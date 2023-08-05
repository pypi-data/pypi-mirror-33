from fabric.operations import run, sudo


def run_or_sudo(cmd, use_sudo, **kwargs):
    runner = sudo if use_sudo else run
    return runner(cmd=cmd, **kwargs)
