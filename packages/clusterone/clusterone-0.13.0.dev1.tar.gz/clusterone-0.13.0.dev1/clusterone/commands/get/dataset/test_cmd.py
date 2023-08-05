from collections import OrderedDict

from click.testing import CliRunner

from clusterone import ClusteroneClient
from clusterone.clusterone_cli import cli
from clusterone.commands.get.dataset import cmd
from clusterone.mocks.dataset import GET_DATASET_TEST


def test_passing_project_path(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    cmd.path_to_dataset = mocker.Mock()

    CliRunner().invoke(cli, ['get', 'dataset', 'some_dataset_name'])

    cmd.path_to_dataset.assert_called_with('some_dataset_name', context=mocker.ANY)

def test_table_call(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    cmd.path_to_dataset = mocker.Mock(return_value=GET_DATASET_TEST)
    cmd.make_table = mocker.Mock(return_value="Example table string")

    CliRunner().invoke(cli, ['get', 'dataset', 'some_dataset_name'])

    cmd.make_table.assert_called_with([
        ('Name', 'test_kwiatek'),
        ('Id', 'ab3d71a8-6c31-40fc-a761-d1b5f7b32729'),
        ('Source', 'gitlab'),
        ('URL', 'https://git.tensorport.com/smeler/test_kwiatek.git'),
        ], header=['Property', 'Value'])

def test_printing_out_table(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    cmd.path_to_dataset = mocker.Mock(return_value=GET_DATASET_TEST)
    cmd.make_table = mocker.Mock(return_value="Example table string")

    result = CliRunner().invoke(cli, ['get', 'dataset', 'some_dataset_name'])

    assert result.output == "Example table string\n"
