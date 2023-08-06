from click.testing import CliRunner

from clusterone import ClusteroneClient
from clusterone.clusterone_cli import cli
from clusterone.just_client import Notebook


def test_command(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    mock_notebook = mocker.Mock()
    mock_notebook.id = "853b9f10-36ce-4de4-b2f8-108d69733b42"
    mocker.patch.object(Notebook, 'from_clusterone', return_value=mock_notebook)

    result = CliRunner().invoke(cli, ['stop', 'notebook', 'dummy'])

    Notebook.from_clusterone.assert_called_with(mocker.ANY, "dummy")
    assert mock_notebook.stop.called
    assert "853b9f10-36ce-4de4-b2f8-108d69733b42\n" in result.output
