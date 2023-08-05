"""
Convention about keys: please use lowercase only
Please make sure to mark configurable properties with is_configurable decorator
"""
# TODO: Move this to general Config

import json
import os

import click
import py
from click.exceptions import BadParameter
from coreapi.exceptions import NetworkError

from clusterone.just_client import ClusteroneClient
from .defaults import CONFIG_DEFAULTS

CONFIGURABLE_PROPERTIES = []
# TODO: Export click Choice type in the future (well, actually Choice from clusterone.utilities)

def is_configurable(function):
    """
    Indicates that this property can be configured by the user
    """

    CONFIGURABLE_PROPERTIES.append(function.__name__)

    return function

class Config(object):
    def __init__(self, defaults=CONFIG_DEFAULTS):
        #TODO: When dropping python2 compliacne add * to function signature

        self.file = py.path.local(
            click.get_app_dir('clusterone')).join('justrc.json')

        self.defaults = defaults

    # if file does not exists create it
    # if file is corrupted and cannot be read / written inform user about this
    #TODO: TEST THIS!!!!!!!!!!

    def __setattr__(self, key, value):
        """
        Normalizes the keys to lowercase only
        """

        return object.__setattr__(self, key.lower(), value)

    # redo this to protected methods
    # do a generic __setattr__ and __getattr__
    def set(self, key, value):
        #TODO: Docstring

        #TODO: Smarter somethign
        #TODO: Check for existing solution
        #TODO: Context manager for json
        #TODO: Don't load and reqrite whole file, do it in a smarter way
        #TODO: Extract to utilities

        dir_path = os.path.dirname(str(self.file))
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        with self.file.open('w+', encoding='utf-8') as justrc:

            try:
                json_content = json.load(justrc)
            except ValueError:
                json_content = {}

            json_content[key] = value

            try:
                # pretty printing is important for the config to be human editable
                justrc.write(json.dumps(json_content, indent=4, sort_keys=True))
            except TypeError:
                # Python 2 compliance - .write() required unicode
                justrc.write(json.dumps(json_content).decode('utf-8'))

    def get(self, key):
        # TODO: OMG, refactor like shit!!!!!!!
        try:
            with self.file.open('r', encoding='utf-8') as justrc:

                try:
                    json_content = json.load(justrc)
                except ValueError:
                    json_content = {}

                return json_content[key]
        except (KeyError, py.error.ENOENT):
            return self.defaults[key]


    #TODO: Can this be done dynamically?
    # yup - __getattr__ or __getattribute__

    #TODO: Move validation from cmd here
    @property
    @is_configurable
    def endpoint(self):
        """
        the URL to Clusterone service
        """

        # TODO: Redo this to [] key aquisition
        return self.get('endpoint')

    @endpoint.setter
    def endpoint(self, value):
        #type (object, str) -> str
        # TODO: Move this to function signature after dropping Python 2.7 compliance

        if not value.endswith('/'):
            value = "{}/".format(value)

        if "api" not in value:
            value = "{}api/".format(value)

        try:
            ClusteroneClient(api_url=value)
        except NetworkError:
            raise BadParameter("please make sure it's a valid URL pointing to Clusterone service.", param_hint="endpoint")

        self.set('endpoint', value)
