from collections import OrderedDict

import pytest
from pytest import raises
from click.exceptions import BadParameter

from clusterone.persistance.session import Session
from clusterone.clusterone_cli import Context
from clusterone.commands.create.job import base_cmd


def test_python_version_aliases(mocker):
    base_cmd.client = mocker.Mock()
    base_cmd.path_to_project = mocker.Mock(return_value={'id': "project-id-123456", "commits": [OrderedDict([('id', '4a82d16c7995856c7973af38f2f5ba4eac0cd2d1')]), OrderedDict([('id', '4a82d16c79elorapc7973af38f2f5ba4eac0cd2d1')])]})
    base_cmd.time_limit_to_minutes = mocker.Mock(return_value=123456)
    session = Session()
    session.load()
    context = Context(None, session, None)

    result = base_cmd.base(context, {'framework': 'tensorflow-130', 'project_path': 'mnist-demo', 'python_version': '3', 'requirements': None, 'commit': 'latest', 'name': 'old-morning-562', 'module': 'mymodule.py', 'package_manager': 'pip', 'package_path': '', 'description': '', 'time_limit': 2880, 'datasets': '',}, module_arguments=())


    assert result['parameters']['python_version'] == '3.6'

    result = base_cmd.base(context, {'framework': 'tensorflow-130', 'project_path': 'mnist-demo', 'python_version': '2', 'requirements': None, 'commit': 'latest', 'name': 'old-morning-562', 'module': 'mymodule.py', 'package_manager': 'pip', 'package_path': '', 'description': '', 'time_limit': 2880, 'datasets': '',}, module_arguments=())


    assert result['parameters']['python_version'] == '2.7'

def test_package_manager_aliases(mocker):
    base_cmd.client = mocker.Mock()
    base_cmd.path_to_project = mocker.Mock(return_value={'id': "project-id-123456", "commits": [OrderedDict([('id', '4a82d16c7995856c7973af38f2f5ba4eac0cd2d1')]), OrderedDict([('id', '4a82d16c79elorapc7973af38f2f5ba4eac0cd2d1')])]})
    base_cmd.time_limit_to_minutes = mocker.Mock(return_value=123456)
    session = Session()
    session.load()
    context = Context(None, session, None)

    result = base_cmd.base(context, {'framework': 'tensorflow-130', 'project_path': 'mnist-demo', 'python_version': '3', 'requirements': None, 'commit': 'latest', 'name': 'old-morning-562', 'module': 'mymodule.py', 'package_manager': 'anaconda', 'package_path': '', 'description': '', 'time_limit': 2880, 'datasets': '',}, module_arguments=())


    assert result['parameters']['package_manager'] == 'conda'

def test_default_requirement_conda(mocker):
    base_cmd.client = mocker.Mock()
    base_cmd.path_to_project = mocker.Mock(return_value={'id': "project-id-123456", "commits": [OrderedDict([('id', '4a82d16c7995856c7973af38f2f5ba4eac0cd2d1')]), OrderedDict([('id', '4a82d16c79elorapc7973af38f2f5ba4eac0cd2d1')])]})
    base_cmd.time_limit_to_minutes = mocker.Mock(return_value=123456)
    session = Session()
    session.load()
    context = Context(None, session, None)

    result = base_cmd.base(context, {'framework': 'tensorflow-1.3.0', 'project_path': 'mnist-demo', 'python_version': '3', 'requirements': None, 'commit': 'latest', 'name': 'old-morning-562', 'module': 'mymodule.py', 'package_manager': 'anaconda', 'package_path': '', 'description': '', 'time_limit': 2880, 'datasets': '',}, module_arguments=())


    assert result['parameters']['requirements'] == 'requirements.yml'


def test_custom_user_arguments(mocker):
    assert base_cmd.validate_module_arguments(mocker.ANY, mocker.ANY, ('--custom-dummy-argument0', 'dummy0', '--custom-dummy-argument1', 'dummy1')) == {'custom-dummy-argument0': 'dummy0', 'custom-dummy-argument1': 'dummy1'}

def test_custom_user_arguemnts_missing_value(mocker):
    with raises(BadParameter):
        base_cmd.validate_module_arguments(mocker.ANY, mocker.ANY, ('--custom-dummy-argument0', '--custom-dummy-argument1', 'dummy1'))
