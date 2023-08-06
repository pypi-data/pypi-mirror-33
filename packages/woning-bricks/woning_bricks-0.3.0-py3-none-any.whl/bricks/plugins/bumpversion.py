from bricks.plugin_kit.base import BasePlugin
from bricks.plugin_kit.checks import (ExecutableInPath,
                                      PythonLibraryIsPresent,
                                      FileExists)


class Plugin(BasePlugin):
    def get_checks(self):
        return [
            ExecutableInPath(
                'bumpversion is available in PATH',
                executable='bumpversion'
            ),
            PythonLibraryIsPresent(
                'bumpversion is installed',
                library='bumpversion'
            ),
            FileExists(
                'Configuration file exists',
                files=(
                    '.bumpversion.cfg',
                    'setup.cfg'
                )
            )
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
