# -*- coding: utf-8 -*-

import click
from clusterone import authenticate

@click.command()
@click.pass_obj
@authenticate()
def command(context):
    """
    Log out from Clusterone
    """

    context.session.delete()
    #TODO: Do a request to API to logout
    #TODO: Test this
    #TODO: Pylint tests
    #TODO: Refactor
    #TODO: Pylint
