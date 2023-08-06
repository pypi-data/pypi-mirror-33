def native_command(name=None):
    def actual_decorator(func):
        func._bricks_command = True
        if name:
            func._bricks_name = name
        return func

    return actual_decorator


class BasePlugin(object):
    def __init__(self):
        self.project = None
        self.namespace = ""

    def get_commands(self):
        """Returns a list of commands for the project"""
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

    def initialize(self):
        """Initializes the project to make sure it is ready to use the plugin

        Eg. if it needs docker-compose, make sure it is available in PATH
        """
        return []

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
