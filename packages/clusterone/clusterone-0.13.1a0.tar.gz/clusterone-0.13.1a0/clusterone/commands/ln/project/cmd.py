import sys

import click
from click.exceptions import MissingParameter, BadParameter

from clusterone import authenticate
from clusterone.utilities import silent_prompt
from .helper import main


def is_data_on_stdin():
    return not sys.stdin.isatty()

@click.command()
@click.option(
    '--project-path',
    '-p',
    help="Project identifier. Format \"username/project\".")
@click.option(
    '--repo-path',
    '-r',
    help="Path to local Git repository.")
@click.pass_obj
@authenticate()
def command(context, project_path, repo_path):
    """
    Links existing Clusterone project with a local Git repository
        Clusterone remote url can be passed through stdin.
    """

    client, session, cwd = context.client, context.session, context.cwd

    # since context cannot be referenced in the deault paramters
    repository_path = repo_path if repo_path is not None else cwd

    if is_data_on_stdin():
        remote_url = silent_prompt()
    else:
        if project_path is None:
            raise MissingParameter(
                "Please provide either of them.",
                param_type="remote link or project-path")

        path_tokens = project_path.split('/')

        if not len(path_tokens) == 2:
            if len(path_tokens) == 1:
                path_tokens = [session.get("username")] + path_tokens
            else:
                raise BadParameter(param_hint="--project-path", message="Please provide a valid project-path. Format: \"username/project\".")

        username, project_name = path_tokens

        project = client.get_project(project_name, username=username)

        remote_url = project.get('git_auth_link')

    main(context, repository_path, remote_url)
    return
