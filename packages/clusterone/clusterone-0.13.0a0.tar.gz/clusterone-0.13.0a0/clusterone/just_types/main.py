"""
Clusterone Click types for use in commands

This is essentially a bridge between Clusterone Python client and Click.
"""
from click import ParamType

from clusterone.just_client import Notebook as JustNotebook
from clusterone import client


class Notebook(ParamType):
    name = "jupyter notebook"

    def convert(self, value, param, ctx):
        return JustNotebook.from_clusterone(client, value)

    def __repr__(self):
        return "Notebook"
