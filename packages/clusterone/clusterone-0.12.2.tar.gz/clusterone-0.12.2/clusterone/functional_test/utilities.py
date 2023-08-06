import json
import logging
import random
import string
from contextlib import suppress
from os import environ
from subprocess import run, PIPE
from time import sleep
from click import progressbar

from coreapi import Client

from .types import UserCredentials

JUST_SHELL_COMMAND = "python3 clusterone/clusterone_cli.py"


def _just(command):
    just_command = "{} {}".format(JUST_SHELL_COMMAND, command)
    return just_command


def call(command, asserted=True):
    command_list = command.split()
    result = run(command_list, stdout=PIPE)

    if asserted:
        exit_code = result.returncode
        assert exit_code == 0, "Command: {} failed".format(command)

    return result.stdout


def just_exec(command):
    logging.debug("calling: {}".format(command))
    return call(_just(command)).decode("utf-8")


def generate_random_credentials():
    salt = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))

    username = "cluster-one-test-{}".format(salt)
    password = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))
    email = '{}@example.com'.format(salt)

    logging.info("generated username: {}".format(username))
    logging.info("generated pass: {}".format(password))

    return UserCredentials(username=username, password=password, email=email)


def authorize_client_via_session_file(client=None):
    """
    This is a hax to perform actions on a system that are not possible via CLI
    """

    with open("{}/.config/clusterone/session.json".format(environ['HOME'])) as session:
        token = json.loads("".join(session.readlines()))['token']

    client.token = token
    client.transport = client.get_transport()
    client.api_client = Client(
        transports=[client.transport], decoders=client.decoders)
    client.api_schema = client.download_schema()

    assert token is not None

    logging.info("token acquired: {}...".format(token[0:10]))


def poll(function, args=(), kwargs=None, timeout=None, interval=None):
    """
    Sometimes we don't know when the results shall be available, we only have a time frame
    """

    kwargs = kwargs or {}

    logging.info("polling for {} with interval of {}s, timeout is: {}s".format(function.__name__, interval, timeout))

    max_tries = int(timeout / interval)

    with progressbar(range(max_tries + 1), label="{}".format(function.__name__)) as try_count:
        for tries in try_count:
            kwargs = kwargs or {}

            with suppress(AssertionError):
                function(*args, **kwargs)
                logging.info("completed after {} retries".format(tries))
                break

            sleep(interval)
        else:
            raise AssertionError("Polling failed for {}({}, {})".format(function.__name__, ",".join(map(str, args)), ",".join(["{}={}".format(key, value) for key, value in zip(kwargs.keys(), kwargs.values())])))
