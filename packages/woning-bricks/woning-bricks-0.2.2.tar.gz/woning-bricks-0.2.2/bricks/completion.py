script = """#/usr/bin/env bash

_bricks_completion()
{
    COMPREPLY=($(bricks __gen_completion_suggestions ${COMP_WORDS[*]}))
}

complete -F _bricks_completion bricks

"""


def get_completion_script():
    return script


def get_nearest_matches(arg, possible_matches):
    matches = []
    for item in possible_matches:
        if item.startswith(arg) and item != arg:
            matches.append(item)
    return matches


def get_completion_words(project, args):
    commands = ['init', 'autocomplete', 'help', 'run']
    if len(args) == 0:
        main_command = ''
        sub_commands = []
    elif len(args) == 1:
        main_command = args[0]
        sub_commands = [] if main_command != 'run' else ['']
    else:
        main_command = args[0]
        sub_commands = args[1:]
    if main_command == 'run':
        proj_commands = project.get_commands_names()
        if sub_commands[-1] in proj_commands:
            sub_commands.append('')
        return get_nearest_matches(sub_commands[-1], proj_commands)
    if not sub_commands:
        return get_nearest_matches(main_command, commands)
    return []
