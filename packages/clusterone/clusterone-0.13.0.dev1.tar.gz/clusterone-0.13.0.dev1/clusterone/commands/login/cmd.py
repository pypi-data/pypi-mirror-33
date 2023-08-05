# -*- coding: utf-8 -*-

import gc

import click
from click import echo

from clusterone.utilities import is_latest_version
from clusterone.client_exceptions import NotSupported

def perform_version_check():
    """
    Prevents any operation on the CLI if it's not up to date
    """

    if not is_latest_version():
        raise NotSupported()

@click.command()
@click.option('--username', '-u', prompt=True)
@click.option('--password', '-p', prompt=True, hide_input=True)
#TODO: Since Click 7.0 there is an show=False keyword avaible, it should be used here
# This is a hack to run version check before the credential prompt
@click.option('--version-validator', is_eager=True, callback=lambda context, param, value: perform_version_check(), help="Please ignore this parameter")
@click.pass_obj
def command(context, username, password, version_validator):
    """
    Log into Clusterone
    """

    client, session = context.client, context.session

    client.api_login(username, password)

    # purgin password literal from memory
    del password
    gc.collect()

    session['token'] = client.token
    session['git_token'] = client.git_token
    session['username'] = client.username

    session.save()
    echo("Login successful")
