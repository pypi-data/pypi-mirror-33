# -*- coding: utf-8 -*-

import click
from click import launch
from clusterone import client


@click.command()
@click.pass_obj
def command(context):
    """
    Open the Matrix in the browser
    """

    #TODO: What if operating in headless mode? What does happens then?
    launch(client.matrix_url)
