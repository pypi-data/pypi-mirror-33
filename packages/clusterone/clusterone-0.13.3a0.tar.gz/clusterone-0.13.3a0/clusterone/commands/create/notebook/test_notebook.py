from click.testing import CliRunner

from clusterone.clusterone_cli import cli
from clusterone import ClusteroneClient
from clusterone.commands.create.notebook import cmd
from clusterone.mocks import GET_FRAMEWORKS_RESPONSE, GET_INSTANCE_TYPES_RESPONSE


# base_options call is not explicitly tested as other tests depend on that call

def test_passing_instance_type(mocker):
    # This mocks will propagate across the tests
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    ClusteroneClient.create_job = mocker.Mock()

    ClusteroneClient.get_frameworks = mocker.Mock(return_value=GET_FRAMEWORKS_RESPONSE)
    ClusteroneClient.get_instance_types = mocker.Mock(return_value=GET_INSTANCE_TYPES_RESPONSE)

    ClusteroneClient.create_job = mocker.Mock()
    cmd.base = mocker.Mock(return_value={'meta': {'name': 'late-moon-758', 'description': ''}, 'parameters': {'package_path': '', 'datasets_set': [], 'requirements': 'requirements.txt', 'time_limit': 2880, 'module': 'main', 'framework': 'tensorflow-1.3.0', 'git_commit_hash': '4a82d16c7995856c7973af38f2f5ba4eac0cd2d1', 'code': 'aaf4de71-f506-48c0-855c-02c7c485c5a4', 'package_manager': 'pip', 'Clusterone_api_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9sZ2llcmRAa2FzcHJvd2ljei5wcm8iLCJ1c2VyX2lkIjo3OTUsImV4cCI6MTUxNzMxNjUzMCwidXNlcm5hbWUiOiJhbGxncmVlZCJ9.IJhEZWwMYf2sjHhoxUsjCj0Xll5CVX-RO3eUqvH7myU', 'python_version': 2.7}})
    cmd.Notebook.__init__ = mocker.Mock()

    CliRunner().invoke(cli, [
        'create',
        'notebook',
        '--project', 'someproject',
        '--instance-type', 'p2.xlarge',
    ])

    args, kwargs = cmd.Notebook.__init__.call_args
    assert args[1]['workers']['slug'] == 'p2.xlarge'


def test_default_instance_type(mocker):
    cmd.client = mocker.Mock()
    cmd.base = mocker.Mock(return_value={'meta': {'name': 'late-moon-758', 'description': ''}, 'parameters': {'package_path': '', 'requirements': 'requirements.txt', 'time_limit': 2880, 'module': 'main', 'tf_version': '', 'framework': 'tensorflow', 'git_commit_hash': '4a82d16c7995856c7973af38f2f5ba4eac0cd2d1', 'code': 'aaf4de71-f506-48c0-855c-02c7c485c5a4', 'package_manager': 'pip', 'Clusterone_api_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9sZ2llcmRAa2FzcHJvd2ljei5wcm8iLCJ1c2VyX2lkIjo3OTUsImV4cCI6MTUxNzMxNjUzMCwidXNlcm5hbWUiOiJhbGxncmVlZCJ9.IJhEZWwMYf2sjHhoxUsjCj0Xll5CVX-RO3eUqvH7myU', 'python_version': 2.7}})
    cmd.Notebook.__init__ = mocker.Mock()

    CliRunner().invoke(cli, [
        'create',
        'notebook',
        '--project', 'someproject',
    ])

    args, kwargs = cmd.Notebook.__init__.call_args
    assert args[1]['workers']['slug'] == 't2.small'


def test_call_to_base(mocker):
    cmd.client = mocker.Mock()
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    cmd.base = mocker.Mock()
    cmd.Notebook.__init__ = mocker.Mock()

    CliRunner().invoke(cli, [
        'create',
        'notebook',
        '--project', 'someproject',
    ])

    assert cmd.base.call_count == 1


def test_is_single(mocker):
    cmd.client = mocker.Mock()
    cmd.base = mocker.Mock(return_value={'meta': {'name': 'late-moon-758', 'description': ''}, 'parameters': {'package_path': '', 'requirements': 'requirements.txt', 'time_limit': 2880, 'module': 'main', 'tf_version': '', 'framework': 'tensorflow', 'git_commit_hash': '4a82d16c7995856c7973af38f2f5ba4eac0cd2d1', 'code': 'aaf4de71-f506-48c0-855c-02c7c485c5a4', 'package_manager': 'pip', 'Clusterone_api_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9sZ2llcmRAa2FzcHJvd2ljei5wcm8iLCJ1c2VyX2lkIjo3OTUsImV4cCI6MTUxNzMxNjUzMCwidXNlcm5hbWUiOiJhbGxncmVlZCJ9.IJhEZWwMYf2sjHhoxUsjCj0Xll5CVX-RO3eUqvH7myU', 'python_version': 2.7}})
    cmd.Notebook.__init__ = mocker.Mock()

    CliRunner().invoke(cli, [
        'create',
        'notebook',
        '--project', 'someproject',
    ])

    args, kwargs = cmd.Notebook.__init__.call_args
    assert args[1]['mode'] == 'single'
    assert args[1]['framework']['slug'] == 'jupyter'


def test_is_client_called(mocker):
    cmd.client = mocker.Mock()
    cmd.base = mocker.Mock(return_value={'meta': {'name': 'late-moon-758', 'description': ''}, 'parameters': {'package_path': '', 'requirements': 'requirements.txt', 'time_limit': 2880, 'module': 'main', 'tf_version': '', 'framework': 'tensorflow', 'git_commit_hash': '4a82d16c7995856c7973af38f2f5ba4eac0cd2d1', 'code': 'aaf4de71-f506-48c0-855c-02c7c485c5a4', 'package_manager': 'pip', 'Clusterone_api_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9sZ2llcmRAa2FzcHJvd2ljei5wcm8iLCJ1c2VyX2lkIjo3OTUsImV4cCI6MTUxNzMxNjUzMCwidXNlcm5hbWUiOiJhbGxncmVlZCJ9.IJhEZWwMYf2sjHhoxUsjCj0Xll5CVX-RO3eUqvH7myU', 'python_version': 2.7}})
    cmd.Notebook.__init__ = mocker.Mock()

    CliRunner().invoke(cli, [
        'create',
        'notebook',
        '--project', 'someproject',
    ])

    assert cmd.Notebook.__init__.called


def test_outputting_notebook_url_and_token(mocker):
    cmd.client = mocker.Mock()
    cmd.base = mocker.Mock(return_value={'meta': {'name': 'late-moon-758', 'description': ''}, 'parameters': {'package_path': '', 'requirements': 'requirements.txt', 'time_limit': 2880, 'module': 'main', 'tf_version': '', 'framework': 'tensorflow', 'git_commit_hash': '4a82d16c7995856c7973af38f2f5ba4eac0cd2d1', 'code': 'aaf4de71-f506-48c0-855c-02c7c485c5a4', 'package_manager': 'pip', 'Clusterone_api_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9sZ2llcmRAa2FzcHJvd2ljei5wcm8iLCJ1c2VyX2lkIjo3OTUsImV4cCI6MTUxNzMxNjUzMCwidXNlcm5hbWUiOiJhbGxncmVlZCJ9.IJhEZWwMYf2sjHhoxUsjCj0Xll5CVX-RO3eUqvH7myU', 'python_version': 2.7}})
    mock_notebook = mocker.Mock()
    mock_notebook.url = "my_dummy_url"
    mock_notebook.token = "token"
    cmd.Notebook.__new__ = mocker.Mock(return_value=mock_notebook)

    result = CliRunner().invoke(cli, [
        'create',
        'notebook',
        '--project', 'someproject',
    ])

    assert result.output == "my_dummy_url\naccess token: token\n"
