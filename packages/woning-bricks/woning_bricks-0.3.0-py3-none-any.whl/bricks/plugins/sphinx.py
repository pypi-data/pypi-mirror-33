from bricks.plugin_kit.base import BasePlugin, native_command
from bricks.plugin_kit.checks import (ExecutableInPath,
                                      PythonLibraryIsPresent,
                                      FileExists)


class Plugin(BasePlugin):
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

    def get_checks(self):
        return [
            PythonLibraryIsPresent('sphinx is installed', 'Sphinx'),
            ExecutableInPath('sphinx-quickstart is in PATH',
                             'sphinx-quickstart'),
            FileExists('docs/ exists', 'docs/'),
            FileExists('docs/Makefile exists', 'docs/Makefile'),
            FileExists('docs/make.bat exists', 'docs/make.bat'),
            FileExists('docs/source/ exists', 'docs/source/'),
            FileExists('docs/source/conf.py exists',
                       'docs/source/conf.py'),
            FileExists('docs/source/index.rst exists',
                       'docs/source/index.rst'),

        ]

    @native_command('open-docs')
    def open_docs(self):
        """Opens the built documentation in the default browser"""
        import webbrowser
        webbrowser.open('docs/build/html/index.html')
