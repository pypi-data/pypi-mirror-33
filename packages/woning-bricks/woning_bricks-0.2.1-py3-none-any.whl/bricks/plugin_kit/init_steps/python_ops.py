import subprocess

import sys

from bricks.exceptions import PluginInitError
from bricks.plugin_kit.init_steps.base import BaseInitStep


class PythonLibraryIsPresent(BaseInitStep):
    def __init__(self, package):
        self.package = package

    def execute(self, project):
        cmd = '{} -mpip install {}'.format(sys.executable, self.package)
        call_res = subprocess.run(cmd, shell=True)
        if call_res.returncode != 0:
            raise PluginInitError('Unable to install {}'.format(self.package))
