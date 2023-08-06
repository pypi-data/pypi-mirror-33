import click
from click import echo

from clusterone.utilities import Choice
from clusterone import client
from clusterone.just_client import Notebook
from clusterone.commands.create.job.base_cmd import job_base_options, base


@job_base_options(project_required=False)
@click.option(
    '--instance-type',
    type=Choice(client.instance_types_slugs),
    default="t2.small",
    help="Type of single instance to run.")
def command(context, custom_arguments, **kwargs):
    """
    Create jupyter notebook
    """

    notebook_configuration = base(context, kwargs, module_arguments=custom_arguments)

    notebook_configuration['parameters']['mode'] = "single"
    notebook_configuration['parameters']['workers'] = \
        {
            'slug': kwargs['instance_type'],
            'replicas': 1
        }

    notebook_configuration['parameters']['framework'] = {'slug': 'jupyter'}

    # flattens notebook_configuration
    _notebook_configuration = notebook_configuration['parameters']
    _notebook_configuration.update(notebook_configuration['meta'])
    notebook_configuration = _notebook_configuration

    notebook = Notebook(client, notebook_configuration)
    echo(notebook.url)
    echo("access token: {}".format(notebook.token))
