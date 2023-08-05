import click

from clusterone import client
from clusterone.utilities import Choice
from .base_cmd import job_base_options, base


@job_base_options()
@click.option(
    '--instance-type',
    type=Choice(client.instance_types_slugs),
    default="t2.small",
    help="Type of instance")
def command(context, custom_arguments, **kwargs):
    """
    Creates a single-node job.
    """

    job_configuration = base(context, kwargs, module_arguments=custom_arguments)

    job_configuration['parameters']['mode'] = "single"
    job_configuration['parameters']['workers'] = \
    {
        'slug': kwargs['instance_type'],
        'replicas': 1
    }

    client.create_job(
        job_configuration['meta']['name'],
        description=job_configuration['meta']['description'],
        parameters=job_configuration['parameters'],
        )
