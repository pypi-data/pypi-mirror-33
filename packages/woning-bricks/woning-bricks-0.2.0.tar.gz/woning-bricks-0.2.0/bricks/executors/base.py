class ExecutionSummary(object):
    def __init__(self, statuses=None):
        self.statuses = statuses or []

    def is_successful(self):
        return all(s == 0 for s in self.statuses)


class BaseExecutor(object):
    def __init__(self, project):
        self.project = project

    def execute_command(self, command, params):
        pass
