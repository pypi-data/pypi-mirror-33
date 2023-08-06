import importlib
import sys

from wattle import Nested, List
from wattle.nodes import String, Choice, ParentReference, Dict

from bricks.exceptions import CommandNotFoundError, PluginInitError
from bricks.executors import get_executor
from bricks.executors.base import ExecutionSummary
from bricks.logger import logger
from bricks.plugin_kit.base import BasePlugin


class ProjectMetadata:
    name = String()
    description = String()
    version = String()
    tags = List(String(), default=list)
    author = String(default="")
    plugins_path = List(String(), default=list)


# noinspection PyTypeChecker
class CommandSpec:
    name = String()
    commands = List(String())
    driver = Choice(['local', 'docker', 'native', 'bricks'])
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
    namespace = String(default="")
    project = ParentReference()

    def get_instance(self):
        try:
            module = importlib.import_module(
                'bricks.plugins.{}'.format(self.name))
        except ImportError:
            module = importlib.import_module(self.name)
        Plugin = module.Plugin
        instance = Plugin(**self.kwargs)
        instance.project = self.project
        instance.namespace = self.namespace
        return instance


# noinspection PyTypeChecker
class Project:
    metadata = Nested(ProjectMetadata)
    plugins = List(Nested(Plugin, collect_unknown='kwargs'), default=list)
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
        self.extend_plugin_path()
        if self.plugins_loaded:
            return
        for plugin in self.plugins:
            plugin_instance = plugin.get_instance()
            for command in plugin_instance.get_all_commands():
                self.commands.append(
                    self.build_command_obj(command, plugin, plugin_instance)
                )
        self.plugins_loaded = True

    def build_command_obj(self, command: dict,
                          plugin: Plugin,
                          plugin_instance: BasePlugin):
        instance = CommandSpec()
        if plugin_instance.namespace:
            instance.name = plugin_instance.namespace + ":" + \
                            command['name']
        else:
            instance.name = command['name']
        instance.driver = command.get('driver', 'local')
        instance.commands = command['commands']
        instance.project = self
        descr = command.get('description')
        if not descr:
            descr = ''
        instance.description = descr
        instance.from_plugin = plugin
        return instance

    def run_checks(self):
        checks_failed = False
        for plugin in self.plugins:
            logger.info('')
            logger.warning('Running checks for {}'.format(plugin.name))
            logger.info('')
            check_result = plugin.get_instance().run_checks()
            if not check_result.successful:
                checks_failed = True
            for check_item in check_result.checks:
                if check_item[1]:
                    logger.error('[\u2718] {} - {}'.format(check_item[0].name,
                                                           check_item[1]))
                else:
                    logger.info('[\u2713] {}'.format(check_item[0].name))
        return not checks_failed

    def extend_plugin_path(self):
        sys.path.append('./bricks_plugins')
        sys.path.extend(self.metadata.plugins_path)
