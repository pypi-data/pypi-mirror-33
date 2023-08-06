from bricks.executors.base import BaseExecutor, ExecutionSummary


class NativeExecutor(BaseExecutor):
    def execute_command(self, command, params):
        try:
            command(**params)
        except Exception as e:
            return str(e)
        else:
            return 0
