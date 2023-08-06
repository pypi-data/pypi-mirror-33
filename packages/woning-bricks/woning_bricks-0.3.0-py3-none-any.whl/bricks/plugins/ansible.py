import os

from bricks.plugin_kit.base import BasePlugin
from bricks.plugin_kit.checks import (FileExists, ExecutableInPath,
                                      PythonLibraryIsPresent,
                                      AtLeastOneFileExists)


class Plugin(BasePlugin):
    def get_commands(self):
        commands = []
        for playbook_name in self.iter_playbooks():
            for env in self.iter_environments():
                commands.append(self.build_command_from_paybook_and_env(
                    playbook_name, env
                ))
        return commands

    def get_checks(self):
        return [
            PythonLibraryIsPresent('ansible is installed', 'ansible'),
            ExecutableInPath('ansible is in PATH', 'ansible'),
            ExecutableInPath('ansible-playbook is in PATH',
                             'ansible-playbook'),
            FileExists('ansible/ exists', 'ansible/'),
            FileExists('ansible/inventories/ exists', 'ansible/inventories'),
            FileExists('ansible/playbooks/ exists', 'ansible/playbooks/'),
            FileExists('ansible/playbooks/ exists', 'ansible/playbooks/'),
            AtLeastOneFileExists(
                'At least one inventory is defined',
                'ansible/inventories/*/hosts'
            ),
            AtLeastOneFileExists(
                'At least a playbook is defined',
                'ansible/playbooks/*.yml'
            )
        ]

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
