from subprocess import call

import pytest

from clusterone.utilities import is_latest_version


@pytest.mark.slow()
def test_clusterone_throws_but_pytest_does_not():
    #TODO: Make it run in the approperiate directory regardless of invocation path
    bashCommand = "python clusterone/clusterone_cli.py"
    exit_code = call(bashCommand, shell=True)

    print("Please visit README-> Development -> Additional naming conventions and note about folder structure -> Caution. This may be a potential solution to your problem. Keep on Clusteronein'!")
    assert exit_code is 0

@pytest.mark.slow()
def test_clusterone_projects_dependency_met():
    """
    Clusterone project depend on 2 functions from the client.
    Thoose function should be properly exposed until further notice
    """

    try:
        from clusterone import get_data_path, get_logs_path
    except ImportError as exception:
        pytest.fail("Clusterone should propperly expose thoose 2 functions")


@pytest.mark.slow()
def test_version():
    """
    Makes sure that the version set in repo is >= the latest pypi version
    """

    assert is_latest_version()

