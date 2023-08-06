import teampy
import os
import __init__
from colorama import init, Fore

import click

def print_teampy():
    print(' _                                   ')
    print('| |_ ___  __ _ _ __ ___  _ __  _   _ ')
    print('| __/ _ \/ _` | \'_ ` _ \| \'_ \| | | |')
    print('| ||  __/ (_| | | | | | | |_) | |_| |')
    print(' \__\___|\__,_|_| |_| |_| .__/ \__, |')
    print('                        |_|    |___/ ')

@click.group()
@click.version_option(teampy.__version__)
def rat():
    """
    Teampy is a collection of tools for team-based learning.

    The rat command is used to create, print, evaluate and give feedback on
    readiness assurance tests.

    """
    pass

#@teampy.command(help='Handle quizzes.')
#@click.option('--new', 'operation', flag_value='new', default=True, help='Create a new quiz.')
#@click.option('--check', 'operation', flag_value='check', help='Check an existing quiz.')
@rat.command()
def new():
    """
    Create templates for a new RAT.
    """
    click.echo('Create a new RAT.')

@rat.command()
#@click.argument('file', type=click.File('r'))
@click.argument('file', type=click.Path(exists=True))
def check(file):
    """
    Check a RAT file for consistency before printing.
    """
    print(type(file))
    print(file)

    cwd = os.getcwd()
    print(cwd)
    from os.path import isfile, join
    j = join(cwd, file)
    abs = os.path.abspath(j)
    dir = os.path.dirname(abs)
    print(dir)
    print(isfile(j))
    print(type(j))
    __init__.rat_check(click.open_file(file), abs)

@rat.command(name='print')
@click.argument('file', type=click.File('r'))
def print_(file):
    """
    Print a RAT before class.
    """
    click.echo('Print the rat')
    print(type(file))

@rat.command()
def eval():
    """
    Evaluate a RAT during class.
    """
    click.echo('Evaluate a RAT.')

if __name__ == "__main__":
    rat()
