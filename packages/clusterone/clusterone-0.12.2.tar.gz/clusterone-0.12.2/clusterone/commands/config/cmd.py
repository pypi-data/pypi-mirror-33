# -*- coding: utf-8 -*-

import click

from clusterone import config
from clusterone.persistance.config import CONFIGURABLE_PROPERTIES
from clusterone.utilities import Choice
from clusterone.utilities import append_to_docstring


@click.command()
@click.pass_obj
@click.argument(
    'key',
    type=Choice(CONFIGURABLE_PROPERTIES),
    )
@click.argument(
    'value',
    )
@append_to_docstring("Available keys: {}".format(", ".join(CONFIGURABLE_PROPERTIES)))
def command(context, key, value):
    """
    Configure the CLI. Config is persistent.

    """

    setattr(config, key, value)
