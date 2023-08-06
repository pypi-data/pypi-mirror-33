"""
Building blocks of a functional tests

Contains high level action as understood by the business.
"""

import subprocess
import logging

from .utilities import just_exec, call, poll
from .types import Output
from coreapi.exceptions import ErrorMessage


def set_endpoint(url):
    just_exec("config endpoint {}".format(url))

    logging.info("using endpoint {}".format(url))


def register_user(user_credentials, client):

    response = client.client_action(['register', 'create'], params={
        'username': user_credentials.username,
        'email': user_credentials.email,
        'password': user_credentials.password,
    }, validate=True)

    assert response['username'] == user_credentials.username, "Registration failure"
    assert response['email'] == user_credentials.email, "Registration failure"

    logging.info("registration complete")


def login(user_credentials):

    output = just_exec(
        "login --username {} --password {}".format(user_credentials.username, user_credentials.password))

    assert "successful" in output, "Login failure"

    logging.info("login completed")


def logout():
    just_exec("logout")

    logging.debug("credentials clear")


def init_gitlab_project_from_clusterone_samples(name, project_url):
    call("git clone -q {}".format(project_url))
    folder_name = project_url.split("/")[-1]
    project_initialization_output = just_exec("init project {} -r ./{}".format(name, folder_name))
    subprocess.call("cd {}; git push -q clusterone".format(folder_name), shell=True)

    assert project_initialization_output.split('\n')[1].endswith('{}.git'.format(name)), "Project creation failure"

    logging.info("local and remote project clone completed")

    # check if commits appeared
    poll(just_exec, args=tuple(["create job single --project {} --name {}".format(name, "test_project_has_commits")]), timeout=60, interval=10)


def create_job(project_name, job_name, module="main", framework=None, dataset=None):

    job_state = just_exec("get jobs")
    assert job_name not in job_state, "???"

    framework = ("--framework {}".format(framework)) if framework else ""
    dataset = "--datasets {}".format(dataset) if dataset else ""

    just_exec("create job distributed --name {} --project {} --module {} --time-limit 1h {} {}".format(job_name, project_name, module, framework, dataset))

    job_state = just_exec("get jobs")
    assert job_name in job_state, "Job creation failure"

    logging.info("job successfully created")


def start_job(project_name, job_name):
    just_exec("start job -p {}/{}".format(project_name, job_name))
    job_status = just_exec("get job {}/{}".format(project_name, job_name))

    assert "starting" in job_status, "Job start failure"

    logging.info("job successfully started")


def check_outputs(desired_outputs, job_name, client=None):

    def download_file(filename):
        response = client.client_action(['jobs', 'file', 'read'], params={
            'job_id': job_id,
            'filename': filename
        }, validate=True)

        return response

    job_data = just_exec("get jobs")
    job_data_parsed = job_data.split()
    job_id = job_data_parsed[job_data_parsed.index("None/{}".format(job_name)) + 2]

    try:
        response = client.client_action(['jobs', 'files', 'list'], params={
            'job_id': job_id,
        }, validate=True)
    except ErrorMessage as exception:

        if "404 Not Found" in str(exception.error):
            outputs = []
        else:
            raise
    else:
        outputs = response[0]['contents']

    if desired_outputs == Output.ANY:
        assert outputs, "ANY output acquisition failure"
    elif desired_outputs == Output.NONE:
        assert outputs == []
    elif desired_outputs == Output.CHECKPOINT:
        assert any({"ckpt" in output_file['name'] for output_file in outputs}), "CHECKPOINT output acquisition failure"
    elif desired_outputs == Output.LOSS:
        for worker_log in {output_file['name'] for output_file in outputs if "worker" in output_file['name'] and output_file['name'].endswith(".txt")}:
            assert "loss" in download_file(worker_log).lower(), "LOSS output acquisition failure"
    else:
        raise ValueError("Desired_outputs parameter must be correct enum value")

    logging.info("outputs match target {}".format(desired_outputs))
