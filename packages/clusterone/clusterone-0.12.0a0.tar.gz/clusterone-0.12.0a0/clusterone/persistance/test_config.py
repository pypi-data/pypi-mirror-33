from pytest import raises
from click.exceptions import BadParameter
from coreapi.exceptions import NetworkError

from clusterone.persistance import config
from clusterone import ClusteroneClient


def test_normalize_config_keys(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    config.Config.__init__ = mocker.Mock(return_value=None)
    config.Config.set = mocker.Mock()
    test_config = config.Config()

    test_config.ENDPOINT = "http://elorap.com/api"

    test_config.set.assert_called_with('endpoint', "http://elorap.com/api/")


def test_endpoint_slash_and_api(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    config.Config.__init__ = mocker.Mock(return_value=None)
    config.Config.set = mocker.Mock()
    test_config = config.Config()

    test_config.endpoint = "http://elorap.com"

    test_config.set.assert_called_with('endpoint', "http://elorap.com/api/")


def test_endpoint_verify_schema(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    config.Config.__init__ = mocker.Mock(return_value=None)
    config.Config.set = mocker.Mock()
    test_config = config.Config()

    test_config.endpoint = "http://elorap.com"

    ClusteroneClient.__init__.assert_called_with(mocker.ANY, api_url="http://elorap.com/api/")


def test_endpoint_invalid_schema_throw(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None, side_effect=NetworkError())
    config.Config.__init__ = mocker.Mock(return_value=None)
    config.Config.set = mocker.Mock()
    test_config = config.Config()

    with raises(BadParameter):
        test_config.endpoint = "http://wrongendpoint.com/api/"
