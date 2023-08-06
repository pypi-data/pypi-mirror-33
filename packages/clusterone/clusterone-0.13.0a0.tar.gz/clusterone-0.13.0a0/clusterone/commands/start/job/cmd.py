# -*- coding: utf-8 -*-

import click
from click.exceptions import MissingParameter, UsageError

from clusterone import authenticate
from clusterone.utilities import path_to_job_id


@click.command()
@click.pass_obj
@authenticate()
@click.option(
    '--job-id',
    '-i',
    help='ID of the job to start.')
@click.option(
    '--job-path',
    '-p',
    help='Path of the job to start. Format: \"username/project/job-path\".')
def command(context, job_path, job_id):
    """
    Runs an existing job, identified either by name or ID
    """

    client = context.client

    if job_path is None and job_id is None:
        raise MissingParameter(
            "Please provide either of them",
            param_type="--job-id or --job-path")

    if job_path is not None and job_id is not None:
        raise UsageError("Please provide either --job-id or --job-path, but NOT both")

    if job_path:
        job_id = path_to_job_id(job_path, context=context)

    client.start_job(job_id)

    return job_id
