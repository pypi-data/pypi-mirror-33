# -*- coding: utf-8 -*-
""" Commands for interacting with the remote service. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import sys

# 3rd party imports
import click

# local imports
from scaffy import remote
from scaffy import scaffold
from scaffy.core import log
from scaffy.scaffold import Scaffold
from . import cli


@cli.command()
@click.option(
    '-u', '--username',
    type=str,
    prompt='Username',
    help='scaffyhub username'
)
@click.option(
    '-p', '--password',
    type=str,
    prompt='Password',
    hide_input=True,
    help='scaffyhub password'
)
@remote.print_api_errors
def login(username, password):
    """ Login to scaffyhub.

    After login the authorization token will be stored in scaffy ~/.config
    directory for future use. The username/password is not stored anywhere and
    once the token expires the user will log again. The app supports rolling
    session so every time you interact with scaffyhub you will get the new token
    and your session time will be extended.
    """
    client = remote.Client()

    client.login(username, password)
    log.info("Logged in")


@cli.command()
@click.argument('name', type=str)
@remote.print_api_errors
def push(name):
    """ Push scaffold to scaffyhub.

    The scaffold file will be uploaded to scaffyhub. You can then pull that
    scaffold from any machine using `scaffy pull`.
    """
    local_store = scaffold.LocalStore()

    item = local_store.load(name)

    print(item.name)
    # Upload the scaffold


@cli.command()
@click.argument('name', type=str)
@remote.print_api_errors
def pull(name):
    """ Pull a scaffold with the given name from scaffyhub. """
    local_store = scaffold.LocalStore()
    api = remote.Client()

    remote_item = api.scaffold.get_by_name(name)

    if remote_item is None:
        log.err("'{}' does not exist".format(name))
        sys.exit(-1)

    temp_path = remote_item.download()
    item = Scaffold.load_from_file(temp_path)

    # This will physically write the scaffold file to a local store, thus
    # making a copy so the original can be deleted.
    local_store.add(item)
    os.remove(temp_path)


@cli.command()
@click.argument('name', type=str)
@click.argument(
    '-o', '--out-path',
    type=click.Path(exists=False, writable=True),
    default='/Users/novo/.config/scaffy/local/test.scaffold'
)
def download(name, out_path):
    """ Download a scaffold from scaffyhub into an arbitrary file. """
    api = remote.Client()
    remote_item = api.scaffold.get_by_name(name)

    if remote_item is None:
        log.err("'{}' does not exist".format(name))
        sys.exit(-1)

    remote_item.download(out_path)
