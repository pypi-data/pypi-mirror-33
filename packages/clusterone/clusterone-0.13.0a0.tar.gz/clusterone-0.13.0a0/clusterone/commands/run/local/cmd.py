import os
import re

import click
from click import Choice, Path
from click import IntRange
from click.exceptions import BadParameter

from clusterone import run_tf

try:
    from math import inf
except ImportError as exception:
    inf = float('inf')

# TODO: Move this to utilities
POSITIVE_INTEGER = IntRange(1, inf)


# TODO: Move this to utilities
def validate_python_identifier(value):
    if not re.match("[_A-Za-z][_a-zA-Z0-9]*$", value):
        raise ValueError("{} is not a valid Python identifier".format(value))

    return value


def validate_module(ctx, param, value, py_identifier_validator=validate_python_identifier):
    value = value.replace("./", "")
    value = value.replace(".py", "")

    try:
        value = py_identifier_validator(value)
    except ValueError:
        raise BadParameter("must be a valid Python identifier")

    return value


def validate_mode(ctx, param, value):
    return "single-node" if value == "single" else value


def validate_env(ctx, param, value):
    return False if value == "new" else True


@click.command()
@click.pass_context
@click.argument(
    "mode",
    type=Choice(["single", "distributed"]),
    callback=validate_mode,
)
@click.option(
    "--module",
    type=Path(exists=True),
    default="./main.py",
    callback=validate_module,
    help="A path to module to run, must be DIRECTLY in CWD, defaults to './main.py'",
)
@click.option(
    "--worker-replicas",
    type=POSITIVE_INTEGER,
    default=2,
    help="Number of worker instances",
)
@click.option(
    "--ps-replicas",
    type=POSITIVE_INTEGER,
    default=1,
    help="Number of parameter server instances",
)
@click.option(
    "--requirements",
    type=Path(exists=True),
    default="./requirements.txt",
    help="A path to requirements file, defaults to './requirements.txt'",
)
@click.option(
    "--env",
    type=Choice(["current", "new"]),
    default="new",
    callback=validate_env,
    help="Environment to run the job in - 'new' rebuilds the environment from scratch"
         " and 'current' reuses the current environment, defaults to 'new'",
)
def command(context, mode, module, env, requirements, worker_replicas, ps_replicas):
    """
    Simulate job runs locally

    MODE [ single | distributed ]
    """

    run_tf(
        cwd=os.getcwd(),
        package_path='',
        module=module,
        mode=mode,
        worker_replicas=worker_replicas,
        ps_replicas=ps_replicas,
        requirements=requirements,
        current_env=env,
    )
