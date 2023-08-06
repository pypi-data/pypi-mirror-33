from click.testing import CliRunner

from clusterone import ClusteroneClient
from clusterone.persistance.session import Session
from clusterone.clusterone_cli import cli
from clusterone.client_exceptions import NotSupported

from clusterone.commands.login import cmd


def test_upgrade_required(mocker):
    """
    PyPi version is newer than current CLI version
    """

    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    mocker.patch.object(Session, 'save', autospec=True, return_value=None)
    ClusteroneClient.api_login = mocker.Mock()
    ClusteroneClient.token = "sample_token"
    ClusteroneClient.username = "username"
    cmd.echo = mocker.Mock()

    cmd.is_latest_version = mocker.Mock(return_value=False)

    result = CliRunner().invoke(cli, ['login'], 'username\npassword',)
    assert isinstance(result.exception, NotSupported)

def test_no_upgrade(mocker):
    """
    PyPi version is the same or older than current CLI version
    """

    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    mocker.patch.object(Session, 'save', autospec=True, return_value=None)
    ClusteroneClient.api_login = mocker.Mock()
    ClusteroneClient.token = "sample_token"
    ClusteroneClient.username = "username"
    cmd.echo = mocker.Mock()

    cmd.is_latest_version = mocker.Mock(return_value=True)
    cmd.perform_version_check = mocker.Mock()

    result = CliRunner().invoke(cli, ['login'], 'username\npassword',)

    assert cmd.perform_version_check.called
    assert result.exception is None

def test_calls(mocker):
    """
    Dependency calls
    """

    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    mocker.patch.object(Session, 'save', autospec=True)
    ClusteroneClient.api_login = mocker.Mock()
    ClusteroneClient.token = "sample_token"
    ClusteroneClient.username = "username"
    cmd.echo = mocker.Mock()

    cmd.is_latest_version = mocker.Mock(return_value=True)

    CliRunner().invoke(cli, ['login'], 'username\npassword',)

    ClusteroneClient.api_login.assert_called_with("username", "password")
    assert Session.save.called
    cmd.echo.assert_called_with("Login successful")
