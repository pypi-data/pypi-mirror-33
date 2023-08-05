import subprocess
import os

from bricks.executors.base import BaseExecutor


class DockerComposeExecutor(BaseExecutor):
    def execute_command(self, command, params):
        docker_command = self.build_command(command)
        new_env = os.environ.copy()
        new_env.update(params)
        proc = subprocess.run(docker_command, shell=True, env=new_env)
        return proc.returncode

    def build_command(self, command):
        name = self.project.metadata.name
        docker_command = 'docker-compose exec {name} {command}'.format(
            name=name,
            command=command)
        return docker_command
