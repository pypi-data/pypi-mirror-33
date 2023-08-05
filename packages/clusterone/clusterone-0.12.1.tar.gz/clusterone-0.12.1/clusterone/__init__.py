from clusterone import client_exceptions, messages

from clusterone.just_client import ClusteroneClient

ClusteroneException = client_exceptions.ClusteroneException
from .auth import authenticate

from clusterone.instances import CLIENT_INSTANCE as client
from clusterone.instances import CONFIG_INSTANCE as config

#TODO: Solve this better at higher level
# to satisfy clusterone projetcs' dependecy
from clusterone.just_client import get_logs_path, get_data_path

__version__ = '0.12.1'
