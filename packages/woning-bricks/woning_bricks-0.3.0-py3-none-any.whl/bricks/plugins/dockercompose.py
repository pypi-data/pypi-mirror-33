from bricks.plugin_kit.base import BasePlugin
from bricks.plugin_kit.checks import ExecutableInPath, FileExists


class Plugin(BasePlugin):

    def __init__(self, docker_compose_yml='docker-compose.yml'):
        self.docker_compose_yml = docker_compose_yml
        super(Plugin, self).__init__()

    def get_checks(self):
        return [
            ExecutableInPath('docker-compose in PATH',
                             executable='docker-compose'),
            FileExists('"{}" exists'.format(self.docker_compose_yml),
                       self.docker_compose_yml)
        ]

    def get_commands(self):
        return [
            self.get_single_command('start', 'up -d'),
            self.get_single_command('stop', 'down'),
            self.get_single_command('logs', 'logs'),
            self.get_single_command('tail', 'logs -f'),
            self.get_single_command('build', 'build'),
            self.get_single_command('pull', 'pull'),
            self.get_single_command('exec', 'exec {} $command'.format(
                self.project.metadata.name)),
        ]

    def get_single_command(self, name, command):
        descr = 'Runs the "{}" docker compose command'.format(
            command.split()[0])
        return self.build_command(
            description=descr,
            name=name,
            driver='local',
            commands=[
                'docker-compose -f {} {}'.format(self.docker_compose_yml,
                                                 command)
            ])
