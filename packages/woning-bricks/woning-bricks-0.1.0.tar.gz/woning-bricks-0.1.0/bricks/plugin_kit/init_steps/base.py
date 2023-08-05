from bricks.exceptions import PluginInitError


class BaseInitStep(object):
    """Base initialization step for plugins"""

    def execute(self, project):
        """Executes the current step.

        Returns:
            True if the step succeeds, an instance of PluginInitError otherwise
            with a proper error message
        """
        pass


class CheckStep(BaseInitStep):
    """Checks if a condition is met."""

    def __init__(self, on_fail=None):
        super(CheckStep, self).__init__()
        self.on_fail = on_fail

    def execute(self, project):
        if self.condition():
            return True
        else:
            if self.on_fail:
                return self.on_fail()
            return PluginInitError(self.get_err_message())

    def condition(self):
        """The condition to be checked against"""
        return False

    def get_err_message(self):
        """Get the error message to be displayed if the condition is false"""
        return ""
