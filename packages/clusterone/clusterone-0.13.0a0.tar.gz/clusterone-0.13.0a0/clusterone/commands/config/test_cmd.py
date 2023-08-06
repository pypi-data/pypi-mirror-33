from click.testing import CliRunner

from clusterone import ClusteroneClient
from clusterone.clusterone_cli import cli
from clusterone.commands.config import cmd
from clusterone.persistance.config import Config
from clusterone.persistance.session import Session


def test_passing(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    mocker.patch.object(Session, 'save', autospec=True, return_value=None)
    mocker.patch.object(Config, '__init__', autospec=True, return_value=None)
    cmd.setattr = mocker.Mock()

    CliRunner().invoke(cli, [
        'config',
        'endpoint',
        'dummy-value',
    ])

    args, kwargs = cmd.setattr.call_args
    assert isinstance(args[0], Config)
    assert args[1] == 'endpoint'
    assert args[2] == 'dummy-value'


def test_non_configurable(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    mocker.patch.object(Session, 'save', autospec=True, return_value=None)
    mocker.patch.object(Config, '__init__', autospec=True, return_value=None)
    cmd.setattr = mocker.Mock()

    result = CliRunner().invoke(cli, [
        'config',
        'dummy-key',
        'dummy-value',
    ])

    assert result.exit_code == 2
