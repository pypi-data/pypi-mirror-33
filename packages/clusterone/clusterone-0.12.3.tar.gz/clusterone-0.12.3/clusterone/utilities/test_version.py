import clusterone
from clusterone.mocks import PYPI_RESPONSE_LITERAL_V0DOT10DOT3

from . import version

PYPI_RESPONSE_LITERAL = {'releases': {'1234567890.0.0': [{}]}}
version.PYPI_VERSIONS_URL = "//some/url/to/pypi"
is_latest_version = version.is_latest_version


def test_up_to_date(mocker):
    clusterone.__version__ = "1234567891.30.51"
    json_mock = mocker.Mock()
    json_mock.json = mocker.Mock(return_value=PYPI_RESPONSE_LITERAL)
    version.requests.get = mocker.Mock(return_value=json_mock)

    assert is_latest_version()


def test_outdated(mocker):
    clusterone.__version__ = "20.0.0"

    is_latest_version = version.is_latest_version

    assert not is_latest_version()


def test_prereleases(mocker):
    """
    Even if there is later prerelease version only the latest stable should be taken into account
    """

    PYPI_RESPONSE_LITERAL = {'releases': {'1.0.2a10': [{}], '1.0.0': [{}]}}
    json_mock = mocker.Mock()
    json_mock.json = mocker.Mock(return_value=PYPI_RESPONSE_LITERAL)
    version.requests.get = mocker.Mock(return_value=json_mock)
    clusterone.__version__ = "1.0.1"

    assert is_latest_version()


def test_propper_sorting(mocker):
    """
    If lexical sorting is used than v9.0.0 would be before v10.0.0
    which is wrong

    Originated from CLUS-365.
    """

    json_mock = mocker.Mock()
    json_mock.json = mocker.Mock(return_value=PYPI_RESPONSE_LITERAL_V0DOT10DOT3)
    version.requests.get = mocker.Mock(return_value=json_mock)
    clusterone.__version__ = "0.10.0"

    assert not is_latest_version()
