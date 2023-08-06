import os.path
import subprocess

from bricks.exceptions import PluginInitError
from bricks.plugin_kit.base import BasePlugin, native_command
from bricks.plugin_kit.init_steps.base import BaseInitStep
from bricks.plugin_kit.init_steps.python_ops import PythonLibraryIsPresent
from bricks.plugin_kit.init_steps.file_ops import EnsureDir


class InitializeSphinx(BaseInitStep):
    def execute(self, project):
        if self.has_makefile() and self.has_conf_file():
            return
        cmd = self.build_cmd(project)
        print(cmd)
        res = subprocess.run(args=cmd, cwd='docs')
        if res.returncode != 0:
            raise PluginInitError('Sphinx init failed')

    def has_makefile(self):
        return os.path.isfile('docs/Makefile')

    def has_conf_file(self):
        return os.path.isfile('docs/conf.py')

    def build_cmd(self, project):
        return [
            'sphinx-quickstart',
            '-q',  # quite, no prompt
            '--sep',
            '-p', project.metadata.name,
            '-a', project.metadata.author or 'unspecified',
            '-v', project.metadata.version,
            '-r', project.metadata.version,
            '-l', 'en',
            '--ext-autodoc',
            '--makefile',
            '--batchfile',

        ]


class Plugin(BasePlugin):
    def initialize(self):
        return [
            PythonLibraryIsPresent('sphinx'),
            EnsureDir('docs'),
            InitializeSphinx()
        ]

    def get_commands(self):
        return [
            self.build_command(
                name='build-docs',
                commands=[
                    'make -C docs/ html'
                ],
                description='Builds the HTML docs in docs/build/html/'
            ),
        ]

    @native_command('open-docs')
    def open_docs(self):
        """Opens the built documentation in the default browser"""
        import webbrowser
        webbrowser.open('docs/build/html/index.html')
