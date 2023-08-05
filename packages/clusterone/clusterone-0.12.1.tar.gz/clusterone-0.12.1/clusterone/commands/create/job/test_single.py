from click.testing import CliRunner

from clusterone.clusterone_cli import cli
from clusterone import ClusteroneClient
from clusterone.commands.create.job import single
from clusterone.mocks import GET_FRAMEWORKS_RESPONSE, GET_INSTANCE_TYPES_RESPONSE


# client call is not explicitly tested as other tests depend on that call
# base_options call is not explicitly tested as other tests depend on that call

def test_passing_instance_type(mocker):
    # This mocks will propagate across the tests
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    ClusteroneClient.create_job = mocker.Mock()

    ClusteroneClient.get_frameworks = mocker.Mock(return_value=GET_FRAMEWORKS_RESPONSE)
    ClusteroneClient.get_instance_types = mocker.Mock(return_value=GET_INSTANCE_TYPES_RESPONSE)

    ClusteroneClient.create_job = mocker.Mock()
    single.base = mocker.Mock(return_value={'meta': {'name': 'late-moon-758', 'description': ''}, 'parameters': {'package_path': '', 'requirements': 'requirements.txt', 'time_limit': 2880, 'module': 'main', 'framework': 'tensorflow-1.3.0', 'git_commit_hash': '4a82d16c7995856c7973af38f2f5ba4eac0cd2d1', 'code': 'aaf4de71-f506-48c0-855c-02c7c485c5a4', 'package_manager': 'pip', 'Clusterone_api_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9sZ2llcmRAa2FzcHJvd2ljei5wcm8iLCJ1c2VyX2lkIjo3OTUsImV4cCI6MTUxNzMxNjUzMCwidXNlcm5hbWUiOiJhbGxncmVlZCJ9.IJhEZWwMYf2sjHhoxUsjCj0Xll5CVX-RO3eUqvH7myU', 'python_version': 2.7}})

    CliRunner().invoke(cli, [
        'create',
        'job',
        'single',
        '--project', 'someproject',
        '--instance-type', 'p2.xlarge',
    ])

    args, kwargs = ClusteroneClient.create_job.call_args
    assert kwargs['parameters']['workers']['slug'] == 'p2.xlarge'


def test_default_instance_type(mocker):
    single.client = mocker.Mock()
    single.client.create_job = mocker.Mock()
    single.base = mocker.Mock(return_value={'meta': {'name': 'late-moon-758', 'description': ''}, 'parameters': {'package_path': '', 'requirements': 'requirements.txt', 'time_limit': 2880, 'module': 'main', 'tf_version': '', 'framework': 'tensorflow', 'git_commit_hash': '4a82d16c7995856c7973af38f2f5ba4eac0cd2d1', 'code': 'aaf4de71-f506-48c0-855c-02c7c485c5a4', 'package_manager': 'pip', 'Clusterone_api_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9sZ2llcmRAa2FzcHJvd2ljei5wcm8iLCJ1c2VyX2lkIjo3OTUsImV4cCI6MTUxNzMxNjUzMCwidXNlcm5hbWUiOiJhbGxncmVlZCJ9.IJhEZWwMYf2sjHhoxUsjCj0Xll5CVX-RO3eUqvH7myU', 'python_version': 2.7}})

    CliRunner().invoke(cli, [
        'create',
        'job',
        'single',
        '--project', 'someproject',
    ])

    args, kwargs = single.client.create_job.call_args
    assert kwargs['parameters']['workers']['slug'] == 't2.small'


def test_call_to_base(mocker):
    single.client = mocker.Mock()
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    single.base = mocker.Mock()
    CliRunner().invoke(cli, [
        'create',
        'job',
        'single',
        '--project', 'someproject',
    ])

    assert single.base.call_count == 1


def test_is_single(mocker):
    single.client = mocker.Mock()
    single.client.create_job = mocker.Mock()
    single.base = mocker.Mock(return_value={'meta': {'name': 'late-moon-758', 'description': ''}, 'parameters': {'package_path': '', 'requirements': 'requirements.txt', 'time_limit': 2880, 'module': 'main', 'tf_version': '', 'framework': 'tensorflow', 'git_commit_hash': '4a82d16c7995856c7973af38f2f5ba4eac0cd2d1', 'code': 'aaf4de71-f506-48c0-855c-02c7c485c5a4', 'package_manager': 'pip', 'Clusterone_api_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9sZ2llcmRAa2FzcHJvd2ljei5wcm8iLCJ1c2VyX2lkIjo3OTUsImV4cCI6MTUxNzMxNjUzMCwidXNlcm5hbWUiOiJhbGxncmVlZCJ9.IJhEZWwMYf2sjHhoxUsjCj0Xll5CVX-RO3eUqvH7myU', 'python_version': 2.7}})

    CliRunner().invoke(cli, [
        'create',
        'job',
        'single',
        '--project', 'someproject',
    ])

    args, kwargs = single.client.create_job.call_args
    assert kwargs['parameters']['mode'] == 'single'
