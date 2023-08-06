from pathlib import Path
from itertools import groupby
from subprocess import check_output
import click


def program(line):
    return line.split()[0]


def number_of_calls(prog_lines):
    return len(list(prog_lines[1]))


def take(n, iter):
    for _, e in zip(range(n), iter):
        yield e

def validate_num_commands(ctx, param, value):
    if value is None or  value > 0:
        return value
    else:
        raise click.BadParameter("num must be a positive number")

def get_history():
    output = check_output(['fish', '-c', 'history']).decode()
    commands = output.split('\n')
    return [c.strip() for c in commands if c.strip()]

def recent_commands(history, num):
    seen_programs = set()
    commands = []
    for command in history:
        program, *rest = command.split()
        seen_programs.add(program)
        if len(seen_programs) > num:
            break
        else:
            commands.append(command)
    return commands

def group_by_command(commands):
    return [
        (program, list(lines))
        for program, lines
        in groupby(sorted(commands), program)
    ]


@click.command()
@click.option('--num', type=int, callback=validate_num_commands)
def main(num):
    history = get_history()
    if num is not None:
        commands = recent_commands(history, num)
    else:
        commands = history
    grouped = group_by_command(commands)
    for command, examples in sorted(grouped, key=number_of_calls):
        print(command)
        for example in take(3, set(examples)):
            print('    ' + example)

if __name__ == '__main__':
    main()
