import shutil
import os.path

from bricks.plugin_kit.init_steps.base import CheckStep


class ExecutableInPath(CheckStep):
    """Checks if an executable is available in PATH"""

    def __init__(self, executable_name, on_fail=None):
        super(ExecutableInPath, self).__init__(on_fail)
        self.name = executable_name

    def condition(self):
        return shutil.which(self.name) is not None

    def get_err_message(self):
        return 'Unable to find {} in path.'.format(self.name)


class FileExists(CheckStep):
    """Checks if a certain file exists."""

    def __init__(self, path, on_fail=None):
        super(FileExists, self).__init__(on_fail)
        self.path = path

    def condition(self):
        return os.path.exists(self.path)

    def get_err_message(self):
        return 'Required file "{}" not found'.format(self.path)
