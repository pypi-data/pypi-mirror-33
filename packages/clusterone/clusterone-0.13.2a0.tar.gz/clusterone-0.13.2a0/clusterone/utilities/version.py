import requests
from distutils.version import LooseVersion

import clusterone

PYPI_VERSIONS_URL = 'https://pypi.python.org/pypi/clusterone/json'

# Pypi converts "-alpha" -> "a", and "-beta" to "b"
PRERELEASE_SUFFIXES = ['dev', 'a', 'b', 'rc']


def is_latest_version():
    """
    Performs version check against Pypi
    """
    # TODO: Move this to function signature after removing 2.7 compliance
    # type: () -> bool

    remote_stable_versions = [LooseVersion(version) for version in get_pypi_versions() if is_stable(version)]
    remote_latest_stable = max(remote_stable_versions)

    current = LooseVersion(clusterone.__version__)

    return current >= remote_latest_stable


def is_stable(version): return not any(suffix in version for suffix in PRERELEASE_SUFFIXES)
# TODO: Move this to function signature after removing 2.7 compliance
# type: str -> bool


def get_pypi_versions():
    # TODO: Move this to function signature after removing 2.7 compliance
    # type: () -> [str]

    response_data = requests.get(PYPI_VERSIONS_URL).json()
    return response_data["releases"].keys()
