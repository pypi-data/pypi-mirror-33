import os.path
from pathlib import Path
from shlex import quote

from fabric.contrib.files import upload_template

from fabkit.util import run_or_sudo


class Template:
    __TEMPLATES_DIR__ = Path.cwd()

    SRC_PATH = None
    DST_PATH = None

    def __init__(self):
        self._params = {}

    def upload(self):
        self._upload(False)

    def upload_as_sudo(self):
        self._upload(True)

    def _upload(self, use_sudo=False):
        src_path = "/%s" % str(self.SRC_PATH.relative_to(self.__TEMPLATES_DIR__))

        dst_path = self.DST_PATH or src_path
        dst_dir = os.path.dirname(dst_path)

        run_or_sudo(f'mkdir -p {quote(dst_dir)}', use_sudo)

        upload_template(src_path, dst_path,
                        use_jinja=True,
                        template_dir=str(self.__TEMPLATES_DIR__),
                        use_sudo=use_sudo,
                        backup=False,
                        context=self._params
                        )
