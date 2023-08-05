from bricks.plugin_kit.base import BasePlugin
from bricks.plugin_kit.init_steps.python_ops import PythonLibraryIsPresent
from bricks.plugin_kit.init_steps.checks import ExecutableInPath
from bricks.plugin_kit.init_steps.file_ops import FileRender

from bricks.plugins.resources.python_library import bumpversion_cfg


class Plugin(BasePlugin):
    def initialize(self):
        return [
            PythonLibraryIsPresent('bumpversion'),
            ExecutableInPath('bumpversion'),
            FileRender('.bumpversion.cfg', bumpversion_cfg)
        ]

    def get_commands(self):
        return [
            self.build_command(
                name='bump-patch',
                commands=['bumpversion patch'],
                description='Bumps the patch (x.y.Z) version number.',
            ),
            self.build_command(
                name='bump-minor',
                commands=['bumpversion minor'],
                description='Bumps the minor (x.Y.z) version number.',
            ),
            self.build_command(
                name='bump-patch',
                commands=['bumpversion major'],
                description='Bumps the major (X.y.z) version number.',
            ),
        ]
