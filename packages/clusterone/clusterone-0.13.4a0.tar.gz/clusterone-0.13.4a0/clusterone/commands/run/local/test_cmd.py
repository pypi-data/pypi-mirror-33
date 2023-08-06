import os
import pytest
from click.testing import CliRunner
from click.exceptions import BadParameter

from clusterone import ClusteroneClient
from clusterone.persistance.session import Session
from clusterone.clusterone_cli import cli

from clusterone.commands.run.local import cmd
from clusterone.commands.run.local.cmd import validate_mode, validate_module, validate_env, validate_package_path


@pytest.mark.parametrize(
    'input, result', [
        ("new", False),
        ("current", True),
    ]
)
def test_validate_env(input, result):
    assert validate_env(None, None, input) == result


@pytest.mark.parametrize(
    'input, result', [
        ("single", "single-node"),
        ("distributed", "distributed"),
    ]
)
def test_validate_env(input, result):
    assert validate_mode(None, None, input) == result


@pytest.mark.parametrize(
    "input, result", [
        ("main.py", "main"),
        ("main", "main"),
        ("yelop", "yelop"),
    ]
)
def test_validate_module_strip_path_characters(input, result):
    assert validate_module(None, None, input) == result


@pytest.mark.parametrize(
    'input, result', [
        (".", ""),
        ("mnist", "mnist"),
        ("mnist/", "mnist"),
        ("something/mnist", "something.mnist"),
        ("folder/something/mnist", "folder.something.mnist"),
        ("even_more/folder/something/mnist", "even_more.folder.something.mnist"),
    ]
)
def test_validate_package_path(input, result):
    assert validate_package_path(None, None, input) == result


def test_command(mocker):

    def create_dummy_file(filename):
        with open(filename, "w") as file:
            file.write("pass\n")

    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    cmd.run_tf = mocker.Mock()
    runner = CliRunner()

    with runner.isolated_filesystem() as isolated_cwd:
        os.mkdir('./mnist')
        create_dummy_file("mnist/my_ml_experiment.py")
        create_dummy_file("ml-requirements.txt")

        result = runner.invoke(cli, [
            "run",
            "local",
            "single",
            "--module", "my_ml_experiment",
            "--worker-replicas", "8",
            "--ps-replicas", "3",
            "--requirements", "./ml-requirements.txt",
            "--env", "new",
            "--package-path", "mnist",
        ])

        # for debugging purposes
        print("Command output:\n", result.output)

        _, kwargs = cmd.run_tf.call_args

        assert kwargs == {
            "cwd": isolated_cwd,
            "mode": "single-node",
            "package_path": "mnist",
            "module": "my_ml_experiment",
            "worker_replicas": 8,
            "ps_replicas": 3,
            "requirements": "./ml-requirements.txt",
            "current_env": False,
        }
