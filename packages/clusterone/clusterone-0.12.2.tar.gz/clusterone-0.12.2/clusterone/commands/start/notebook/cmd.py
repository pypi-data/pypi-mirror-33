import click
from click import echo

from clusterone import authenticate
from clusterone.just_types import Notebook
from clusterone import client


@click.command()
@click.pass_obj
@authenticate()
@click.argument(
    'notebook',
    type=Notebook(),
)
def command(context, notebook):
    """
    Starts an existing notebook

    NOTEBOOK: path or uuid of an existing notebook
    """

    notebook.start(client)
    echo(notebook.id)
