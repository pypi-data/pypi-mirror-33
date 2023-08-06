import glob

import shutil
import os.path

from bricks.plugin_kit.base import BaseCheck
from bricks.exceptions import PluginCheckFailedError


class ExecutableInPath(BaseCheck):
    def __init__(self, name, executable):
        self.executable = executable
        super(ExecutableInPath, self).__init__(name)

    def run(self):
        if shutil.which(self.executable) is None:
            raise PluginCheckFailedError('"{}" not found in PATH'.format(
                self.executable
            ))


class PythonLibraryIsPresent(BaseCheck):
    def __init__(self, name, library):
        self.library = library
        super(PythonLibraryIsPresent, self).__init__(name)

    def run(self):
        try:  # for pip >= 10
            from pip._internal.utils.misc import get_installed_distributions
        except ImportError:  # for pip <= 9.0.3
            from pip import get_installed_distributions

        if not any(p.project_name == self.library for p in
                   get_installed_distributions()):
            raise PluginCheckFailedError(
                '"{}" not installed.'.format(self.library))


class FileExists(BaseCheck):
    def __init__(self, name, files):
        if isinstance(files, str):
            self.files = [files]
        else:
            self.files = files
        super(FileExists, self).__init__(name)

    def run(self):
        if not any([os.path.exists(f) for f in self.files]):
            if len(self.files) == 1:
                msg = '"{}" does not exist'.format(self.files[0])
            else:
                msg = 'At least one of {} must exist'.format(
                    ', '.join(self.files))
            raise PluginCheckFailedError(msg)


class AtLeastOneFileExists(BaseCheck):
    def __init__(self, name, glob_expr):
        self.glob_expr = glob_expr
        super(AtLeastOneFileExists, self).__init__(name)

    def run(self):
        files = glob.glob(self.glob_expr)
        if len(files) == 0:
            raise PluginCheckFailedError(
                'At least one file matching {} must exist'.format(
                    self.glob_expr))
