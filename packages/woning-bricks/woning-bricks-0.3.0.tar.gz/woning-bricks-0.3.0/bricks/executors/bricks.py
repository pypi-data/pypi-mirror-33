from bricks.executors.base import BaseExecutor
from bricks.helpers import build_params


class BricksExecutor(BaseExecutor):
    """Executor for composed bricks commands

    **Usage**

    - name: composed_command
      driver: bricks
      description: Example
      commands:
        - test
        - lint -p strict=1

    Then, when running ``bricks run composed_command``, it will run the
    specified commands with the given parameters.

    ** Useful cases **

    Repetitive commands with minor differences.

    - name: deploy_prod
      driver: bricks
      commands:
      - test
      - deploy -p env=prod -p secrets=s3://prod-secrets

    - name: deploy_staging
      driver: bricks
      commands:
      - test
      - deploy -p env=staging -p secrets=s3://staging-secrets
    """

    def execute_command(self, command, params):
        split = command.split('-p', maxsplit=1)
        if len(split) == 2:
            cmd, *raw_params = split
        else:
            cmd = split[0]
            raw_params = []
        return 0 if self.project.run_command(
            cmd.strip(), build_params([rp.strip() for rp in raw_params])
        ).is_successful() else 1
