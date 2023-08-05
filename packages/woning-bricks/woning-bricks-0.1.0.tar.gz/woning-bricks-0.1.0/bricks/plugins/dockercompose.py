from bricks.plugin_kit.base import BasePlugin
from bricks.plugin_kit.init_steps.checks import ExecutableInPath, FileExists

reference = {
    'start': 'Start the containers in the background',
    'stop': 'Stop the containers',
    'logs': 'Show the latest logs (output of the running containers)',
    'tail': 'Show the latest logs continuously',
    'build': 'Force rebuild the local images for the defined services',
    'pull': 'Pulls the latest images for the defined services',
    'exec': 'Executes the command passed in the "command" parameter'
}


class Plugin(BasePlugin):
    reference = reference

    def __init__(self, project):
        super(Plugin, self).__init__(project)

    def initialize(self):
        return [
            ExecutableInPath('docker-compose'),
            FileExists('docker-compose.yml')
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
        return self.build_command(
            name=name,
            driver='local',
            commands=[
                'docker-compose {}'.format(command)
            ])
