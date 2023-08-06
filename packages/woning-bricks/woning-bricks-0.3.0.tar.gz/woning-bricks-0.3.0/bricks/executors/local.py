import subprocess
import os

from bricks.executors.base import BaseExecutor


class LocalExecutor(BaseExecutor):
    """Executor that runs command locally, in a shell

    The parameters are exposed as environment variables
    """
    def execute_command(self, command, params):
        new_env = os.environ.copy()
        new_env.update(params)
        proc = subprocess.run(command, shell=True, env=new_env)
        return proc.returncode
