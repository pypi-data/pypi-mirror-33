from clusterone import ClusteroneClient

from clusterone.persistance.config import Config
from clusterone.persistance.session import Session


SESSION_INSTANCE=Session()
SESSION_INSTANCE.load()

CONFIG_INSTANCE = Config()

CLIENT_INSTANCE = ClusteroneClient(
    token=SESSION_INSTANCE.get('token'),
    username=SESSION_INSTANCE.get('username'),
    api_url=CONFIG_INSTANCE.endpoint
)

