class BricksError(Exception):
    pass


class CommandNotFoundError(BricksError):
    def __init__(self, project, command_name):
        msg = "Command {} not found for project {}".format(
            command_name, project.metadata.name)
        super(CommandNotFoundError, self).__init__(msg)


class DriverNotRecognizedError(BricksError):
    def __init__(self, driver_name):
        msg = "Driver '{}' not recognized".format(driver_name)
        super(DriverNotRecognizedError, self).__init__(msg)


class PluginError(BricksError):
    pass


class PluginInitError(PluginError):
    pass
