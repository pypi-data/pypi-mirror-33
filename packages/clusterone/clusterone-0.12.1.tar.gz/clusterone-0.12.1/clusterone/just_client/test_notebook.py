from coreapi.document import Error
from coreapi.exceptions import ErrorMessage
from pytest import raises

from clusterone.client_exceptions import _NonExistantNotebook, NonExistantNotebook, DuplicateNotebookName
from clusterone.just_client.types import TaskStatus
from clusterone.mocks import NOTEBOOK_JOB_CONFIGURATION, NOTEBOOK_API_RESPONSE
from .notebook import Notebook, NotebookPath


def test_existing_from_uuid(mocker):
    mock_client = mocker.Mock()
    mock_client.client_action.return_value = NOTEBOOK_API_RESPONSE

    target = Notebook._from_data(NOTEBOOK_API_RESPONSE)

    notebook = Notebook.from_clusterone(mock_client, "853b9f10-36ce-4de4-b2f8-108d69733b42")
    args, kwargs = mock_client.client_action.call_args

    assert notebook == target
    assert args[0] == ['notebooks', 'read']
    assert kwargs['params'] == {
        'job_id': "853b9f10-36ce-4de4-b2f8-108d69733b42",
    }


def test_existing_from_path(mocker):
    mock_client = mocker.Mock()
    mock_client.client_action.return_value = NOTEBOOK_API_RESPONSE

    target = Notebook._from_data(NOTEBOOK_API_RESPONSE)

    notebook = Notebook.from_clusterone(mock_client, "dummy/winter-leaf-119")
    args, kwargs = mock_client.client_action.call_args

    assert notebook == target
    assert args[0] == ['notebook_by_name', 'read']
    assert kwargs['params'] == {
        "display_name": "winter-leaf-119",
        "username": "dummy",
    }


def test_existing_from_path_without_username(mocker):
    mock_client = mocker.Mock()
    mock_client.client_action.return_value = NOTEBOOK_API_RESPONSE
    mock_client.username = "dummy"

    Notebook.from_clusterone(mock_client, "winter-leaf-119")
    args, kwargs = mock_client.client_action.call_args

    assert kwargs['params']['username'] == "dummy"


def test_failed_acquisition_by_name(mocker):
    mock_client = mocker.Mock()
    mock_client.client_action.side_effect = ErrorMessage(
        Error(title='404 Not Found', content={'detail': 'Notebook not found'}))

    with raises(NonExistantNotebook):
        Notebook.from_clusterone(mock_client, "dummy/winter-leaf-119")


def test_failed_acquisition_by_id(mocker):
    mock_client = mocker.Mock()
    mock_client.client_action.side_effect = ErrorMessage(
        Error(title='404 Not Found', content={'detail': 'Notebook not found'}))

    with raises(_NonExistantNotebook):
        Notebook.from_clusterone(mock_client, "853b9f10-36ce-4de4-b2f8-108d69733b42")


def test_new(mocker):
    mock_client = mocker.Mock()
    mock_client.client_action.return_value = NOTEBOOK_API_RESPONSE

    target = Notebook._from_data(NOTEBOOK_API_RESPONSE)

    assert Notebook(mock_client, NOTEBOOK_JOB_CONFIGURATION) == target

    args, kwargs = mock_client.client_action.call_args
    assert args[0] == ['notebooks', 'create']
    assert kwargs['params'] == {
        'repository': None,
        'display_name': 'snowy-surf-115',
        'description': '',
        'parameters': NOTEBOOK_JOB_CONFIGURATION,
        'datasets_set': [],
    }


def test_failed_creation(mocker):
    mock_client = mocker.Mock()
    mock_client.client_action.side_effect = ErrorMessage(Error(title='400 Bad Request', content={
        ' messages': [' Fields username and display_name must make a unique set.']}))
    with raises(DuplicateNotebookName):
        Notebook(mock_client, NOTEBOOK_JOB_CONFIGURATION)


def test_initialisation():
    test_notebook = Notebook.__new__(Notebook)
    test_notebook._initialize(NOTEBOOK_API_RESPONSE)

    assert test_notebook.id == "853b9f10-36ce-4de4-b2f8-108d69733b42"
    assert test_notebook.url == "http://853b9f10-36ce-4de4-b2f8-108d69733b42.jupyter.v2.clusterone.com"
    assert test_notebook.status == TaskStatus.created
    assert test_notebook.token == '85c88d21-fb18-42be-8a1a-f73da4585a02'


def test_from_data_constructor():
    template = Notebook.__new__(Notebook)
    template._initialize(NOTEBOOK_API_RESPONSE)

    target = Notebook._from_data(NOTEBOOK_API_RESPONSE)

    assert template == target


def test_starting(mocker):
    mock_client = mocker.Mock()
    test_notebook = Notebook._from_data(NOTEBOOK_API_RESPONSE)

    test_notebook.start(mock_client)

    assert test_notebook.status == TaskStatus.started
    args, kwargs = mock_client.client_action.call_args
    assert args[0] == ['notebooks', 'start']
    assert kwargs['params'] == {
        'job_id': '853b9f10-36ce-4de4-b2f8-108d69733b42',
    }


def test_stopping(mocker):
    mock_client = mocker.Mock()
    test_notebook = Notebook._from_data(NOTEBOOK_API_RESPONSE)

    test_notebook.stop(mock_client)

    assert test_notebook.status == TaskStatus.stopped
    args, kwargs = mock_client.client_action.call_args
    assert args[0] == ['notebooks', 'stop']
    assert kwargs['params'] == {
        'job_id': '853b9f10-36ce-4de4-b2f8-108d69733b42',
    }


def test_repr():
    test_notebook = Notebook._from_data(NOTEBOOK_API_RESPONSE)

    assert repr(test_notebook) == "Notebook(<client_instance>, '853b9f10-36ce-4de4-b2f8-108d69733b42')"


def test_parsing_notebook_path():
    assert Notebook._parse_notebook_path("username/notebook") == NotebookPath(username="username", notebook_name="notebook")
    assert Notebook._parse_notebook_path("notebook") == NotebookPath(username=None, notebook_name="notebook")

    with raises(ValueError):
        Notebook._parse_notebook_path("keton/keton/keton/keton")

    with raises(ValueError):
        Notebook._parse_notebook_path("/")
