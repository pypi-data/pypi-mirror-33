import pytest
from click.testing import CliRunner
from click.exceptions import BadParameter

from clusterone import ClusteroneClient
from clusterone.persistance.session import Session
from clusterone.clusterone_cli import cli

from clusterone.commands.run.local import cmd
from clusterone.commands.run.local.cmd import validate_python_identifier, validate_mode, validate_module, validate_env


def invoke(parameters, mocker):
    """
    Tiny wrapper for native Click runner, provides output information on failure
    """

    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    cmd.run_tf = mocker.Mock()

    result = CliRunner().invoke(cli, ['run', 'local'] + parameters)

    # for debugging purposes
    print("Command output:", result.output)

    _, kwargs = cmd.run_tf.call_args

    return kwargs


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
    "input", [
        "_vaLid",
        "__PytHon_",
        "__identI5fiEr",
        "Pl1ac5holder1111_",
    ]
)
def test_to_python_identifier_valid(input):
    validate_python_identifier(input)


@pytest.mark.parametrize(
    "input", [
        "1invalid",
        "Python!",
        "id_$%^ntifier"
        "also-hyphens-are-not-ok",
    ]
)
def test_to_python_identifier_invalid(input):
    with pytest.raises(ValueError):
        validate_python_identifier(input)


@pytest.mark.parametrize(
    "input, result", [
        ("./main.py", "main"),
        ("main.py", "main"),
        ("./main", "main"),
        ("main", "main"),
        ("yelop", "yelop"),
    ]
)
def test_validate_module_strip_path_characters(input, result):
    assert validate_module(None, None, input) == result


def test_validate_module_valid_python_identifier(mocker):
    mocked_validator = mocker.Mock(return_value="output_value")

    assert validate_module(None, None, "my_input_value", py_identifier_validator=mocked_validator) == "output_value"
    mocked_validator.assert_called_once_with("my_input_value")


def test_validate_module_invalid_python_identifier(mocker):
    mocked_validator = mocker.Mock(side_effect=ValueError)

    with pytest.raises(BadParameter):
        validate_module(None, None, "my_input_value", py_identifier_validator=mocked_validator)

#def test_bla1(mocker):
#    """
#
#    """
#
#    result = invoke(['single'], mocker)
#    assert result["mode"] == "single-node"
