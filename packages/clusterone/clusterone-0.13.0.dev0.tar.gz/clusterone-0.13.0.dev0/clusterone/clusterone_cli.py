#!/usr/bin/env python3

import os
import sys
import logging

import click
import click_log

from clusterone import authenticate

from clusterone.persistance.session import Session
from clusterone import __version__
from clusterone.utils import render_table, info

# TODO: Handle KeyBoardInterrup at high level here

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME_DIR = os.getcwd()
logger = logging.getLogger(__name__)

# Bunch of global messages
session = Session()
session.__init__()
session.load()
if session.get('username') is None:
    owner_help_message = 'Specify owner by usernames'
else:
    owner_help_message = 'Specify owner by username, default: %s' % session.get(
        'username')

pass_config = click.make_pass_decorator(Session, ensure=True)


class Context(object):
    def __init__(self, client, session, cwd):
        self.client = client
        self.session = session
        self.cwd = cwd


from clusterone import ClusteroneException
from clusterone.utilities import log_error


from clusterone import client

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.pass_context
def cli(context):
    """
    Welcome to the Clusterone Command Line Interface.
    """

    config = Session()
    config.load()
    context.obj = Context(client, config, HOME_DIR)


def main():
    try:
        cli()
    except ClusteroneException as exception:
        log_error(exception)
        sys.exit(exception.exit_code)
    # TODO: THIS
    #except Exception as exception:
    # here Sentry logger is a good idea
    #    pass

# ---------------------------------------

@cli.group()
@click_log.simple_verbosity_option()
@click_log.init(__name__)
@click.pass_obj
def get(context):
    """
    < project(s) | dataset(s) | job(s) | events >
    """
    pass


@cli.group()
@click_log.simple_verbosity_option()
@click_log.init(__name__)
@click.pass_obj
def create(context):
    """
    < project | dataset | job >
    """
    pass


@cli.group()
@click.pass_obj
def rm(context):
    """
    < project | dataset | job >
    """
    pass


@create.group()
@click.pass_obj
def job(context):
    """
    < single | distributed >
    """

    pass


@cli.group()
@click.pass_context
def init(context):
    """
    < project | dataset >
    """
    pass


@cli.group()
@click.pass_context
def ln(config):
    """
    < project | dataset >
    """
    pass


@cli.group()
@click.pass_context
def start(config):
    """
    < job | notebook >
    """
    pass


@cli.group()
@click.pass_context
def stop(config):
    """
    < job | notebook >
    """
    pass


# TODO: Redo the above to be dynamic -> eg. job command goes through it's modules and lists single | distributed dynamically

# ------------------------

# TODO: Redo this to dynamic import
from clusterone import commands

get.add_command(commands.get.job.command, 'job')
get.add_command(commands.get.events.command, 'events')

create.add_command(commands.create.project.command, 'project')
create.add_command(commands.create.notebook.command, 'notebook')

job.add_command(commands.create.job.single.command, 'single')
job.add_command(commands.create.job.distributed.command, 'distributed')

rm.add_command(commands.rm.job.command, 'job')
rm.add_command(commands.rm.project.command, 'project')
rm.add_command(commands.rm.dataset.command, 'dataset')

get.add_command(commands.get.project.command, 'project')
get.add_command(commands.get.dataset.command, 'dataset')

init.add_command(commands.init.project.command, 'project')

ln.add_command(commands.ln.project.command, 'project')
ln.add_command(commands.ln.dataset.command, 'dataset')

start.add_command(commands.start.job.command, 'job')
start.add_command(commands.start.notebook.command, 'notebook')

create.add_command(commands.create.dataset.command, 'dataset')

stop.add_command(commands.stop.job.command, 'job')
stop.add_command(commands.stop.notebook.command, 'notebook')

cli.add_command(commands.login.command, 'login')
cli.add_command(commands.logout.command, 'logout')

cli.add_command(commands.matrix.command, 'matrix')
cli.add_command(commands.config.command, 'config')

# ------------------------

@click.command()
@click.option(
    '--owner', default=session.get('username'), help=owner_help_message)
# @click_log.simple_verbosity_option()
# @click_log.init(__name__)
@click.pass_obj
@authenticate()
def get_jobs(context, owner):
    """
    List jobs
    """
    config = context.session

    # TODO: filter by owner name is not working
    running_jobs = client.get_jobs(params={'owner': owner})
    if running_jobs:
        data = []
        data.append(['#', 'Name', 'Id', 'Project', 'Status', 'Launched at'])

        i = 0
        valid_jobs = []
        for job in running_jobs:
            try:
                data.append([
                    i,
                    '%s/%s' % (job.get('owner'), job.get('display_name')),
                    job['job_id'],
                    '%s/%s:%s' %
                    (job.get('repository_owner'), job.get('repository_name'),
                     job.get('git_commit_hash')[:8]),
                    job.get('status'),
                    '' if job.get('launched_at') is None else job.get(
                        'launched_at')[:-5]
                ])
                i += 1
                valid_jobs.append(job)
            except Exception as exception:
                pass
        table = render_table(data, 36)
        click.echo(table.table)
        return running_jobs
    else:
        click.echo(info("You don't seem to have any jobs yet. Try just create job to make one."))
        return


get.add_command(get_jobs, 'jobs')

@click.command()
@authenticate()
@click.pass_obj
@click.option('--owner')
def get_projects(context, owner=None):
    """
    List projects
    """

    config = context.session

    # TODO: fix owner

    projects = client.get_projects()

    if projects:
        click.echo(info("All projects:"))
        data = []
        data.append(
            ['#', 'Project', 'Created at', 'Description'])

        i = 0
        for project in projects:
            try:
                data.append([
                    i,
                    "%s/%s" % (project.get('owner')
                               ['username'], project.get('name')),
                    project.get('created_at')[:19],
                    project.get('description')
                ])
                i += 1
            except:
                pass
        table = render_table(data, 36)
        click.echo(table.table)
        return projects
    else:
        click.echo(info(
            "No projects found. Use 'just create project' to start a new one."))
        return None


get.add_command(get_projects, 'projects')


@click.command()
@click.option('--owner')
@click_log.simple_verbosity_option()
@click_log.init(__name__)
@click.pass_obj
@authenticate()
def get_datasets(context, owner=None):
    """
    List datasets
    """
    client, config = context.client, context.session

    datasets = client.get_datasets(owner)

    if datasets:
        click.echo(info("All datasets:"))
        data = []
        data.append(
            ['#', 'Dataset', 'Modified at', 'Description'])

        i = 0
        for project in datasets:
            try:
                data.append([
                    i,
                    "%s/%s" % (project.get('owner')
                               ['username'], project.get('name')),
                    project.get('modified_at')[:19],
                    project.get('description')
                ])
                i += 1
            except:
                pass
        table = render_table(data, 36)
        click.echo(table.table)
        return datasets
    else:
        click.echo("It doesn't look like you have any datasets yet. You can create a new one with 'just create dataset'.")
        return None


get.add_command(get_datasets, 'datasets')






# TODO: Manage this -> this code is from former run job command

# @click.option('--local', is_flag=True, default=False, help='Run the job locally. Works both with distributed or single-node.')

# local=None,

#    if local:
#        run_local_tf(package_path, module, training_mode, worker_replicas,
#                     ps_replicas, requirements, current_env, framework_version)

#def run_local_tf(package_path, module, training_mode, worker_replicas,
#                 ps_replicas, requirements=None, current_env=False, tf_version=None):
#    # Select training mode
#    training_modes = ['single-node', 'distributed']
#    if (training_mode is None) or (not training_mode in training_modes):
#        if not training_mode:
#            mode = click.echo(question('Select a training mode from'))
#        else:
#            mode = click.echo(
#                question('%s is not a valid training mode. Select from' %
#                         training_mode))
#        for i, mode in enumerate(training_modes):
#            click.echo('%s | %s' % (i, mode))
#        mode_id = select_valid_index(0,
#                                     len(training_modes) - 1,
#                                     question("Select training mode from"))
#        training_mode = training_modes[mode_id]
#
#    if training_mode == 'distributed':
#        # Specify number of workers
#        if worker_replicas == None:
#            worker_replicas = click.prompt(
#                text=question('Select number of workers'), default=1)
#        else:
#            worker_replicas = int(worker_replicas)
#        # Specify number of parameter servers
#        if ps_replicas == None:
#            ps_replicas = click.prompt(
#                text=question('Select number of parameter servers'), default=1)
#        else:
#            ps_replicas = int(ps_replicas)
#
#    # Specify module
#    if module is None:
#        module = click.prompt(
#            text=question('Specify the python module to run'),
#            default='main')
#
#    if not current_env:
#        if requirements is None:
#            choice = select_valid_index(0, 2,
#                                        question(
#                                            "Requirements file not specified. You can \n    0- Specify a requirements file\n    1- Run without installing any requirements\n    2- Use your current environment (not recommended).\n -> Which one do you want?"))
#            if choice == 0:
#                current_env = False
#                requirements = click.prompt(
#                    text=question('Specify the requirements file'),
#                    default='requirements.txt')
#                requirements = os.path.join(os.getcwd(), requirements)
#            elif choice == 1:
#                current_env = False
#                requirements = None
#            elif choice == 2:
#                current_env = True
#
#    if tf_version is None:
#        tf_version = '1.0.0'
#
#    print("Running %s locally" % training_mode)
#    assert (training_mode in ['single-node', 'distributed'])
#    run_tf(
#        cwd=os.getcwd(),
#        package_path=package_path,
#        module=module,
#        mode=training_mode,
#        worker_replicas=worker_replicas,
#        ps_replicas=ps_replicas,
#        requirements=requirements,
#        current_env=current_env,
#        tf_version=tf_version)


#@cli.command()
#@click.argument('path', type=click.Path(exists=True, file_okay=False, resolve_path=True))
#@click.option('--job-id')
#@click_log.simple_verbosity_option()
#@click_log.init(__name__)
#@click.pass_obj
#@authenticate()
#def download_files(context, path, job_id=None):
#    """
#    downloads all outputs and saves at specified path
#    """
#    config, client = context.session, context.client
#    try:
#        # We get list of user jobs and allow user to select them
#        if not job_id:
#            jobs = client.get_jobs()
#            if jobs:
#                job_id, job_name = select_job(jobs, 'Select the job you want to download files from')
#            else:
#                click.echo(
#                    info(
#                        "You do not seem to have any jobs. Use 'tport run' to run a job."
#                    ))
#                return
#        else:
#            job = client.get_job(params={'job_id': job_id})
#            if job:
#                job_id = job.get('job_id')
#                job_name = job.get('display_name')
#            else:
#                click.echo(info("%s is not a valid job id." % job_id))
#                return
#        # Download file list
#        job_file_list = client.get_file_list(job_id)
#        counter = 0
#        for file in job_file_list:
#            counter += 1
#            # Display the files
#            click.echo(
#                option('%s | %s | %s kb' % (counter, file['name'], file['size'] / 1024)))
#            try:
#                if file['size'] > 0:
#                    # Save file in specified path
#                    file_content = client.download_file(job_id, file['name'])
#                    file_path = os.path.join(path, file['name'])
#                    f = open(file_path, "w")
#                    f.write(file_content)
#                    f.close()
#
#            except Exception as e:
#                click.echo("Failed to download files: %s" % str(e))
#                logger.error("Failed to download file: %s" % str(e), exc_info=True)
#                continue
#
#    except Exception as e:
#        logger.error("Failed to download files", exc_info=True)
#        return


if __name__ == '__main__':
    main()
