import os

from bricks.plugin_kit.base import BasePlugin
from bricks.plugin_kit.init_steps.python_ops import PythonLibraryIsPresent
from bricks.plugin_kit.init_steps.checks import ExecutableInPath
from bricks.plugin_kit.init_steps.file_ops import FileRender, EnsureDir


class Plugin(BasePlugin):
    def initialize(self):
        return [
            PythonLibraryIsPresent('ansible'),
            ExecutableInPath('ansible'),
            ExecutableInPath('ansible-playbook'),
            EnsureDir('ansible'),
            EnsureDir('ansible/playbooks'),
            EnsureDir('ansible/inventories'),
            FileRender('ansible/inventories/dev/hosts', ''),
        ]

    def get_commands(self):
        commands = []
        for playbook_name in self.iter_playbooks():
            for env in self.iter_environments():
                commands.append(self.build_command_from_paybook_and_env(
                    playbook_name, env
                ))
        return commands

    def iter_playbooks(self):
        for filename in os.listdir('ansible/playbooks'):
            if filename.endswith('.yml'):
                yield filename.rsplit('.', maxsplit=1)[0]

    def iter_environments(self):
        for dirname in os.listdir('ansible/inventories'):
            if os.path.isdir(os.path.join('ansible/inventories', dirname)):
                yield dirname

    def build_command_from_paybook_and_env(self, playbook_name, env):
        return self.build_command(
            name='ansible-{}-{}'.format(env, playbook_name),
            commands=[
                'ansible-playbook '
                '-i ansible/inventories/{}/hosts '
                'ansible/playbooks/{}.yml'.format(env, playbook_name)
            ],
            description='Runs the "{}.yml" Ansible playbook using the '
                        '"ansible/invetories/{}/hosts" inventory'.format(
                playbook_name, env)
        )
