from bricks.exceptions import PluginCheckFailedError


def native_command(name=None):
    if callable(name):
        raise RuntimeError('It seems you used @native_command instead of '
                           '@native_command()')

    def actual_decorator(func):
        func._bricks_command = True
        if name:
            func._bricks_name = name
        return func

    return actual_decorator


class _CheckResult(object):
    def __init__(self):
        self.checks = []
        self.successful = True

    def add_check_fail(self, check, message):
        self.checks.append((check, message))
        self.successful = False

    def add_check_ok(self, check):
        self.checks.append((check, None))


class BaseCheck(object):
    def __init__(self, name, **kwargs):
        self.name = name

    def run(self):
        raise NotImplementedError()


class BasePlugin(object):
    def __init__(self):
        self.project = None
        self.namespace = ""

    def get_commands(self):
        """Returns a list of commands for the project"""
        return []

    def get_checks(self):
        """Returns a list of checks for the plugin"""
        return []

    def get_native_commands(self):
        native_commands = []
        for attrname in dir(self):
            attrval = getattr(self, attrname)
            if getattr(attrval, '_bricks_command', False):
                # is a bricks command
                native_commands.append({
                    'name': getattr(attrval, '_bricks_name', attrval.__name__),
                    'driver': 'native',
                    'commands': [attrval],
                    'description': attrval.__doc__
                })
        return native_commands

    def get_all_commands(self):
        return self.get_commands() + self.get_native_commands()

    def run_checks(self):
        check_result = _CheckResult()
        for check in self.get_checks():
            try:
                check.run()
            except PluginCheckFailedError as check_error:
                check_result.add_check_fail(check, str(check_error))
            else:
                check_result.add_check_ok(check)
        return check_result

    @staticmethod
    def build_command(commands, name, driver='local', description=None):
        """Builds a command to be added to the pool of available commands."""
        return {
            'driver': driver,
            'name': name,
            'commands': commands,
            'description': description
        }

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<Plugin {}>'.format(self.__module__)
