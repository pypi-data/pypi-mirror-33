# -*- coding: utf-8 -*-
# pylint: disable=unused-import
""" The application entry point.

Setup completion and import all commands.
"""
from __future__ import absolute_import, unicode_literals

# local imports
from scaffy.commands import cli
__all__ = [
    'cli'
]


try:
    # Only enabled click_completion if psutil package is installed
    import psutil
    import click_completion
    click_completion.init()
except ImportError:
    pass


from scaffy.commands import basic   # noqa
from scaffy.commands import remote  # noqa
