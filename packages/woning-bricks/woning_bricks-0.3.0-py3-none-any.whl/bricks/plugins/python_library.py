from glob import glob

import sys

from bricks.plugin_kit.base import BasePlugin, native_command
from bricks.plugin_kit.checks import ExecutableInPath, \
    PythonLibraryIsPresent, FileExists


class Plugin(BasePlugin):
    def get_checks(self):
        return [
            # pytest checks
            PythonLibraryIsPresent('Pytest is installed', 'pytest'),
            ExecutableInPath('pytest is in PATH', 'pytest'),
            FileExists('Tests directory exists', 'tests/'),
            # pycodestyle
            PythonLibraryIsPresent('PyCodeStyle is installed', 'pycodestyle'),
            ExecutableInPath('pycodestyle is in PATH', 'pycodestyle'),
            # distribution
            PythonLibraryIsPresent('Twine is installed', 'twine'),
            ExecutableInPath('Twine is in PATH', 'twine'),
            FileExists('setup.py exists', 'setup.py')
        ]

    def get_commands(self):
        return [
            self.build_command(
                commands=['pytest tests/'],
                name='test',
                driver='local',
                description="Runs the tests from tests/ using pytest."
            ),
            self.build_command(
                name='lint',
                driver='local',
                commands=['pycodestyle .'],
                description="Check code quality using pycodestyle "
                            "(formerly pep8)"
            ),
            self.build_command(
                name='build-dist',
                driver='local',
                commands=['{} setup.py sdist bdist_wheel'.format(
                    sys.executable)],
                description="Builds the distributable packages "
                            "(sdist, bdist and bdist_wheel)"
            ),
            self.get_twine_upload_command()
        ]

    def get_twine_upload_command(self):
        version = self.project.metadata.version
        filenames = glob('dist/*{}*'.format(version))
        return self.build_command(
            name='upload',
            driver='local',
            commands=['twine upload ' + ' '.join(filenames)],
            description="Uploads the last built packages to PiPy"
        )
