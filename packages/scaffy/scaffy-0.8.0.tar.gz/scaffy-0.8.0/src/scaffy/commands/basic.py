# -*- coding: utf-8 -*-
""" Basic commands.
TODO:
    - Add optional fields.
        - On creating you specify pairs of name_in_src=field_name, The marker
          must include the field name somehow.
        - On applying during the read, once a marker is encountered the first
          time, the user us prompted for the value. Then that value is used
          for all subsequent occurrences.
"""
from __future__ import absolute_import, unicode_literals

import json
from os.path import abspath, basename

# 3rd party imports
import click
from six import string_types

# local imports
from scaffy import remote
from scaffy import scaffold
from scaffy.core import log
from scaffy.core import git
from . import cli


DirPath = click.Path(file_okay=False, dir_okay=True, exists=True)


def marker_def(string):
    """ A simple parameter type to define scaffold markers.

    This will parse a marker in format 'name=value[,other]' to a tuple
    (str, str) of name/value pairs. If there are multiple values, the second
    element in the tuple will be a list of string
    """
    name, value = string.split('=')
    name = name.strip()
    value = value.strip()

    if ',' in value:
        value = value.split(',')

    return (name, value)


@cli.command('create')
@click.argument('name', type=str, required=True,)
@click.argument('src_dir', type=DirPath)
@click.option(
    '-e',
    '--exclude',
    multiple=True,
    metavar='PATTERN',
    help=('Exclude patterns. To specify multiple patters supply this option '
          'multiple times.')
)
@click.option(
    '-m', '--marker', 'markers',
    type=marker_def,
    multiple=True,
    metavar='NAME=VALUE(S)',
    help=('Markers that will be created in the scaffold. Supply each marker '
          'using -m name=value1,value2 format. In the above example, every '
          "occurrence of either 'value1' or 'value2' will be replaced with "
          "marker named 'name'. The marker will be replaced with real value "
          "when the scaffold is applied (a project is generated)."
          "This also applies to file and directory names.")
)
@click.option(
    '--no-gitignore',
    is_flag=True,
    help=('If given, .gitignore will not be read for exclude patterns.')
)
@click.option(
    '-v', '--verbose',
    count=True,
    help="Be more verbose."
)
def create(name, src_dir, markers, exclude, no_gitignore, verbose):
    """ Create new scaffold from a source directory.

    This command will create a new scaffold with the given name from the
    supplied src_dir. A template is just a collection of files, some of them
    with markers. The markers are generated during the scaffold creation (this
    command) and later replaced with real values when the apply command is used.

    The scaffold is created in the local store. To list all scaffolds in the
    local store, use scaffy list. It can also be pushed to scaffy hub so it
    can be accessed from any machine.

    Example:

        \033[1mscaffy create my-scaffold . -e dist -e build \033[0m

    The above call will create a scaffold with name 'my-scaffold' and contents
    of the current directory except for files/dirs matching 'dist' and 'build'
    """
    log.info("Creating scaffold ^35{}".format(name))

    store = scaffold.LocalStore()

    markers = dict(markers)
    markers.setdefault('name', basename(abspath(src_dir)))

    if verbose:
        log.info("Exclude")
        for pattern in sorted(exclude):
            log.info("    ^0{}", pattern)

    if not no_gitignore:
        git_exclude = git.load_gitignore(src_dir)
        exclude = set(exclude) | set(git_exclude) | {'.git'}

        if verbose:
            log.info("Exclude from .gitignore")
            for pattern in sorted(git_exclude):
                log.info("    ^0{}", pattern)

    if name is None:
        name = markers['name']
        if not isinstance(name, string_types):
            name = name[0]      # name is a list of names, pick the first one.

    item = scaffold.Scaffold.create(src_dir, name, exclude, markers)
    store.add(item)


@cli.command('info')
@click.argument('name', type=str, required=True)
@click.option(
    '-f', '--files', 'show_files',
    is_flag=True,
    help=('Show the list of files in the scaffold')
)
@click.option(
    '-c', '--config', 'show_config',
    is_flag=True,
    help=('Show scaffold config')
)
def info(name, show_files, show_config):
    """ Show details about a given scaffold

    Example:

        \033[1mscaffy info -cf my-scaffold \033[0m

    This will show the full information about 'my-scaffold' scaffold. This
    includes the scaffold config as well as a list of scaffold files.
    """
    store = scaffold.LocalStore()
    item = store.load(name)

    log.info("Name:     ^33{}", item.name)
    log.info("Size:     ^33{} kb", round(item.size / 1024))
    log.info("Created:  ^33{}", item.pretty_created)

    if show_config:
        log.cprint("Config: {")
        for key, value in item.json_config.items():
            log.cprint('  "{name}": ^33{value}^0'.format(
                name=key, value=json.dumps(value, indent=2)
            ))

        log.cprint("}")

    if show_files:
        log.info("Files:")
        for path in item.files:
            if path in item.marked_files:
                log.info('  ^0{}', path)
            else:
                log.info('  ^90{}', path)


@cli.command('delete')
@click.argument('name', type=str, required=True)
@click.option(
    '-r', '--remote',
    is_flag=True,
    help="When set, the delete will be performed on the hub instead of locally"
)
@remote.print_api_errors
def delete(name, remote):
    """ Delete the selected scaffold locally or from the hub.

    When called without the --remote option, it will delete the scaffold from
    the local store. When called with --remote, it will remove it on the hub
    (and leave the local store copy alone, if it exists).
    """
    log.info("Deleting ^35{}".format(name))
    store = scaffold.LocalStore()
    store.delete(name)


@cli.command('list')
@click.option(
    '-r', '--remote', 'show_remote',
    is_flag=True,
    help="When set, it will show the remote scaffolds instead of local."
)
@click.option(
    '-a', '--all', 'show_all',
    is_flag=True,
    help="When set, This will show both local and remote scaffolds."
)
@remote.print_api_errors
def list_scaffolds(show_remote, show_all):
    """ List scaffolds locally or on the hub. """
    api = remote.Client()
    local = scaffold.LocalStore()

    if show_all or not show_remote:
        log.cprint("^32Local:\n^0")
        for item in local.scaffolds:
            log.cprint("  ^90{}  ^0{}", item.created, item.name)

        log.cprint('')

    if show_all or show_remote:
        scaffolds = api.scaffold.list()

        log.cprint("^32Remote:\n^0")
        for item in scaffolds:
            log.cprint("  ^90{}  ^0{}", item.created, item.name)

        log.cprint('')


@cli.command('apply')
@click.argument('name', type=str)
@click.argument('project_name', type=str)
@click.option(
    '-o', '--out-path',
    type=DirPath,
    default='.',
    help=("Specify the path where the new project will be created. The"
          "project folder will be created within the given path.")
)
def apply_scaffold(name, project_name, out_path):
    """ Generate project using the given scaffold.

    The project will have all the scaffold contents with 'name' markers replaced
    by project_name. Be default, the project folder will be created inside the
    current working directory. This can be changed using the --out-path option.
    """
    store = scaffold.LocalStore()
    item = store.load(name)
    item.apply(proj_name, out_path)
