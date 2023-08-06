from textwrap import dedent, indent

import click


def create_color_func(color):
    def func(*args, **kwargs):
        return click.style(*args, fg=color, **kwargs)

    return func


red = create_color_func('red')
green = create_color_func('green')
yellow = create_color_func('yellow')
cyan = create_color_func('cyan')


class ProjectHelpPrinter(object):
    def __init__(self, project):
        self.project = project
        project.load_plugins()

    def print_help(self):
        click.echo(dedent("""
        Project {name} (version {version})
        {title_underline}

        {description}

        Commands
        --------

        """.format(
            name=green(self.project.metadata.name),
            title_underline='=' * (19 + len(self.project.metadata.name) + len(
                self.project.metadata.version)),
            version=green(self.project.metadata.version),
            description=yellow(self.project.metadata.description),
        )) + self.generate_commands_help())

    def generate_commands_help(self):
        cmds = []
        for command in self.project.commands:
            current_cmd = '- ' + green(command.name)
            if command.from_plugin:
                current_cmd += ' (from {})'.format(
                    cyan(command.from_plugin.name))
                current_cmd += '\n'
            current_cmd += indent(dedent(command.description), '    ')
            current_cmd += '\n'
            cmds.append(current_cmd)
        return '\n'.join(cmds)
