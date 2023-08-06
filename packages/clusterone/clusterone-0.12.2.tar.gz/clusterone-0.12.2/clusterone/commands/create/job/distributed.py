try:
    from math import inf
except ImportError as exception:
    inf = float('inf')

import click
from click import IntRange
from click.exceptions import BadParameter

from clusterone import client
from clusterone.utilities import Choice
from .base_cmd import job_base_options, base

PS_REPLICAS_WARNING_THRESHOLD = 5
WORKER_REPLICAS_WARNING_THRESHOLD = 10

# TODO: Move this to utilities
POSITIVE_INTEGER = IntRange(1, inf)


@job_base_options()
@click.option(
    '--worker-type',
    type=Choice(client.instance_types_slugs),
    default="t2.small",
    help="Type of worker instances")
@click.option(
    '--ps-type',
    type=Choice(client.ps_type_slugs),
    default="t2.small",
    help="Type of parameter server instances")
@click.option(
    '--worker-replicas',
    type=POSITIVE_INTEGER,
    default=2,
    help="Number of worker instances",
)
@click.option(
    '--ps-replicas',
    type=POSITIVE_INTEGER,
    default=1,
    help="Number of parameter server instances",
)
def command(context, custom_arguments, **kwargs):
    """
    Creates a distributed job.
    """

    client = context.client
    job_configuration = base(context, kwargs, module_arguments=custom_arguments)

    job_configuration['parameters']['mode'] = "distributed"

    ps_replicas, worker_replicas = kwargs['ps_replicas'], kwargs['worker_replicas']

    if ps_replicas > PS_REPLICAS_WARNING_THRESHOLD:
        click.echo("Caution: You are creating a job with more than {} parameter servers.".format(PS_REPLICAS_WARNING_THRESHOLD))
    if worker_replicas > WORKER_REPLICAS_WARNING_THRESHOLD:
        click.echo("Caution: You are creating a job with more than {} workers.".format(WORKER_REPLICAS_WARNING_THRESHOLD))

    # TODO: Levearge dynamic frameworks here - requires API support - framework should have a list of supported modes
    # TODO: Test this
    if job_configuration['parameters']['framework']['slug'] == 'pytorch-1.0.0':
        raise BadParameter("PyTorch is only supported for single jobs. For PyTorch please use `create job single [...]` instead.", param_hint="--framework")

    job_configuration['parameters']['workers'] = \
        {
            'slug': kwargs['worker_type'],
            'replicas': worker_replicas,
        }

    job_configuration['parameters']['parameter_servers'] = \
        {
            'slug': kwargs['ps_type'],
            'replicas': ps_replicas,
        }

    client.create_job(
        job_configuration['meta']['name'],
        description=job_configuration['meta']['description'],
        parameters=job_configuration['parameters'],
    )
