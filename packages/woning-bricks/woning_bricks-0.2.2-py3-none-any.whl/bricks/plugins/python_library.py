import os.path
from glob import glob

import sys

from bricks.plugin_kit.base import BasePlugin, native_command
from bricks.plugin_kit.init_steps.file_ops import FileRender
from bricks.plugin_kit.init_steps.python_ops import PythonLibraryIsPresent
from bricks.plugins.resources.python_library import (setup_py_template,
                                                     requirements_dev,
                                                     bumpversion_cfg,
                                                     default_test_py)


class Plugin(BasePlugin):
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

    def initialize(self):
        project_name = self.project.metadata.name
        return [
            PythonLibraryIsPresent('pytest'),
            PythonLibraryIsPresent('twine'),
            PythonLibraryIsPresent('pycodestyle'),
            FileRender('setup.py', setup_py_template),
            FileRender(os.path.join(project_name, '__init__.py'), ''),
            FileRender(os.path.join('tests', '__init__.py'), ''),
            FileRender(os.path.join('tests', 'test_default.py'),
                       default_test_py),
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
