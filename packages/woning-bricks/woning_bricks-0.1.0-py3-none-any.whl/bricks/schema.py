import importlib

from wattle import Nested, List
from wattle.nodes import String, Choice, ParentReference, Dict

from bricks.exceptions import CommandNotFoundError, PluginInitError
from bricks.executors import get_executor
from bricks.executors.base import ExecutionSummary
from bricks.logger import logger


class ProjectMetadata:
    name = String()
    description = String()
    version = String()
    tags = List(String())
    author = String(default="")


# noinspection PyTypeChecker
class CommandSpec:
    name = String()
    commands = List(String())
    driver = Choice(['local', 'docker', 'native'])
    project = ParentReference()
    description = String(default="")

    from_plugin = None

    def execute(self, params):
        status_codes = []
        executor = get_executor(self.driver, self.project)
        for command in self.commands:
            logger.info('Executing command "{}" ({})'.format(
                command, self.driver))
            status_code = executor.execute_command(command, params)
            status_codes.append(status_code)
            if status_code != 0:
                logger.warning(
                    'Command {} ({}) failed with {}. '
                    'Aborting execution'.format(
                        command, self.driver, status_code))
                return ExecutionSummary(status_codes)
            else:
                logger.info('Command {} ({}) ran successfully'.format(
                    command, self.driver
                ))
        return ExecutionSummary(status_codes)


class Plugin:
    name = String()
    params = Dict(default=dict)
    project = ParentReference()

    def get_instance(self):
        module = importlib.import_module('bricks.plugins.{}'.format(self.name))
        Plugin = module.Plugin
        return Plugin(self.project, **self.params)


# noinspection PyTypeChecker
class Project:
    metadata = Nested(ProjectMetadata)
    plugins = List(Plugin, default=[])
    commands = List(CommandSpec)

    def __init__(self):
        self.plugins_loaded = False

    def run_command(self, command_name, params):
        if not self.plugins_loaded:
            self.load_plugins()
        for command in self.commands:
            if command.name == command_name:
                log_str = 'Running {} with params {}'.format(
                    command_name, params)
                logger.info(log_str)
                return command.execute(params)
        raise CommandNotFoundError(self, command_name)

    def get_commands_names(self):
        if not self.plugins_loaded:
            self.load_plugins()
        commands = []
        for command in self.commands:
            commands.append(command.name)
        return commands

    def load_plugins(self):
        if self.plugins_loaded:
            return
        for plugin in self.plugins:
            plugin_instance = plugin.get_instance()
            for command in plugin_instance.get_all_commands():
                command_obj = CommandSpec()
                command_obj.name = command['name']
                command_obj.driver = command.get('driver', 'local')
                command_obj.commands = command['commands']
                command_obj.project = self
                descr = command.get('description')
                if descr is None:
                    descr = plugin.get_instance().get_reference_for(
                        command['name'])
                command_obj.description = descr
                command_obj.from_plugin = plugin
                self.commands.append(command_obj)
        self.plugins_loaded = True

    def initialize_plugins(self):
        init_failed = False
        for plugin in self.plugins:
            logger.info('Initializing {}'.format(plugin.name))
            for step in plugin.get_instance().initialize():
                result = step.execute(self)
                if isinstance(result, PluginInitError):
                    logger.error(str(result))
                    init_failed = True
            if init_failed:
                logger.error('Initialization failed')
            else:
                logger.info('Done.')
        return not init_failed
