import shlex
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader


def get_default_path(parent, name):
    return Path(parent).joinpath(Path(name)) if parent else Path(name)


def check_if_safe(path, out_dir):
    """Check if a given path is within out_dir, raise an exception if it is not"""
    if not str(out_dir.joinpath(path).resolve()).startswith(str(out_dir.resolve())):
        raise IOError('Trying to write to a path outside of the out directory',
                      str(out_dir.resolve()), str(path.resolve()))
    return True


def get_expanded(path, file_name, options):
    """Render a template found at path/filename with the given options"""
    return Environment(loader=FileSystemLoader(path)).get_template(file_name).render(**options)


def prompt_for_choice(_choices, parent):
    """Prompt for a single value which is contained in _choices"""
    click.echo(f'Choose an option for {parent} from:\n{", ".join(_choices)}')
    return click.prompt('Your choice', type=click.Choice(_choices))


def prompt_for_list(default, parent):
    """Prompt for a list of values, seperated by spaces"""
    return click.prompt(f'Override the list {parent}?'
                              f'\nEnter a space seperated list, default: {" ".join(default)}',
                              default=' '.join(default), show_default=False)


def get_list_input(user_list):
    """Handle the user input for a space seperated list and create a normal list"""
    return shlex.split(user_list)


def prompt_for_input(default, parent):
    """Prompt for a single value"""
    return click.prompt(f'Override {parent}?'
                        f'\nDefault {default}', default=default, show_default=False, type=type(default))
