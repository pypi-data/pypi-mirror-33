from uuid import UUID
from coreapi.exceptions import ErrorMessage
from collections import namedtuple

from clusterone.just_client.types import TaskStatus
from clusterone.client_exceptions import _NonExistantNotebook, NonExistantNotebook, DuplicateNotebookName


NotebookPath = namedtuple("NotebookPath", "notebook_name username")


class Notebook(object):
    """
    Handle of jupyter notebook
    """

    def _initialize(self, api_response):
        """
        This works as __init__

        For production code make sure that the passed data is real, up to date response from Clusterone API
        """

        self.url = api_response['notebook_url']
        self.id = api_response['job_id']
        self.status = TaskStatus(api_response['status'])
        self.token = api_response['parameters']['token']

    def __init__(self, client, configuration):
        """
        Create a brand new notebook and return a handle

        The method is overwritten to have nice API, see _initialize for initialisation
        """

        params = {
                'repository': configuration['code'],
                'display_name': configuration['name'],
                'description': configuration['description'],
                'parameters': configuration,
                'datasets_set': configuration['datasets_set'],
            }

        try:
            params['git_commit_hash'] = configuration['git_commit_hash']
        except KeyError:
            pass

        try:
            response = client.client_action(['notebooks', 'create'], params=params)
        except ErrorMessage as exception:
            if "400" in exception.error.title:
                raise DuplicateNotebookName()
            else:
                raise

        self._initialize(response)

    @classmethod
    def _from_data(cls, api_response):
        """
        Alternate constructor that bypasses calling __init__ and uses _initialize instead

        Also: might be useful for testing.
        """

        # to avoid triggering __init__
        bare_instance = cls.__new__(cls)

        bare_instance._initialize(api_response)
        return bare_instance

    @classmethod
    def from_clusterone(cls, client, path_or_uuid):
        """
        Obtains the handle of existing jupyter notebook from Clusterone.

        The handle can be obtained by providing either uuid or path.
        """

        try:
            UUID(path_or_uuid)
        except ValueError:
            notebook_path = cls._parse_notebook_path(path_or_uuid)

            request_target = "notebook_by_name"
            request_params = {
                "display_name": notebook_path.notebook_name,
                # if explicit username is not provided use the currently logged user
                "username": notebook_path.username or client.username,
            }
            not_found_exception = NonExistantNotebook
        else:
            request_target = "notebooks"
            request_params = {
                'job_id': path_or_uuid,
            }
            not_found_exception = _NonExistantNotebook

        try:
            response = client.client_action([request_target, 'read'], params=request_params)
            # no need to check for duplicates, the notebook name is guaranteed to be unique by the backend
        except ErrorMessage as exception:
            if "404" in exception.error.title:
                raise not_found_exception()
            else:
                raise

        return cls._from_data(response)

    @staticmethod
    def _parse_notebook_path(path_string):
        """
        Extracts notebook name and optionally username from user provided string
        """

        parsed_path_components = path_string.split('/')

        if len(parsed_path_components) > 2:
            raise ValueError("Path string not conforming to the 'username/notebook_name' or 'notebook_name' format")

        if not parsed_path_components[0]:
            raise ValueError("Notebook name cannot be empty")

        try:
            return NotebookPath(username=parsed_path_components[0], notebook_name=parsed_path_components[1])
        except IndexError:
            return NotebookPath(username=None, notebook_name=parsed_path_components[0])

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return "Notebook(<client_instance>, {!r})".format(self.id)

    def start(self, client):
        client.client_action(['notebooks', 'start'], params={
            'job_id': self.id,
        })

        self.status = TaskStatus.started

    def stop(self, client):
        client.client_action(['notebooks', 'stop'], params={
            'job_id': self.id,
        })

        self.status = TaskStatus.stopped
