# -*- coding: utf-8 -*-


import os

import click
import coreapi
import py
from coreapi import Client
from coreapi import codecs
from coreapi import transports
from coreapi.auth import TokenAuthentication

from clusterone import client_exceptions
from clusterone.client_exceptions import WrongNumberOfGPUs, NoCommitsInProjectFound
from clusterone.utilities import lazy_property

# Python 2.7 compliance
try:
    from functools import lru_cache
except ImportError as exception:
    def identity(*args, **kwargs):
        """
        A dummy decorator that does nothing
        """

        def wrapper(function):
            """
            Like literally waste of space...
            """
            return function

        return wrapper


    lru_cache = identity

LOCAL_DEV = True if os.environ.get('JUST_DEBUG', 'False').upper() == "TRUE" else False


def get_data_path(dataset_name, local_root, local_repo, path):
    """
    Depending on the environment (clusterone cloud vs local) update path to data.
    Args:
        dataset_name: string, Clusterone dataset repository name, e.g. clusterone/mnist
        local_root: string, specifies the root directory for dataset.
              e.g. /home/username/datasets
        local_repo: string, specifies the repo name inside the root data path.
              e.g. mnist
        path: string, specifies the path inside the repository, (optional)
              e.g. train
    Returns:
        if code is running locally this function returns:
            local_root/local_repo/path
        if code runs on clusterone cloud this function returns:
            /data/dataset_name/path
    """
    #TODO: DO THIS PROPPERLY!!!!!!
    #environment = os.environ['CLUSTERONE_CLOUD']

    environment = os.environ.get('CLUSTERONE_CLOUD') or os.environ.get('TENSORPORT_CLOUD')
    environment = 'clusterone-cloud' if environment else "local"

    #TODO: Hotfixing TEN-819
    # Have no way of manually testing this
    # This should have a propper test case
    # Handling should be abstracted to a function - as it's the same here and in get_logs_path(root)
    # Need to show intent -> this is for platform indenpendence: converting Windows-style paths to UNIX-style paths. Both ways
    # Eg. /like/this/one <-> C:\like\this\one

    local_root = os.path.abspath(local_root)

    path = path.lstrip("/")  # preventing problems with user input

    if environment == 'local':
        return os.path.join(local_root, local_repo, path)
    elif environment == 'clusterone-cloud':
        return os.path.join('/data/', dataset_name, path)
    else:
        print("Environment is not valid. Assuming local.")
        return os.path.join(local_root, local_repo, path)


def get_logs_path(root):
    """
    Depending on the environment (clusterone cloud vs local) update path to logs.
    Args:
        root: string, specifies the directory for logs.
              e.g. /home/username/logs/mnist...
    Returns:
    """

    #TODO: See get_data_path() for more into, hotfixing TEN-819
    root = os.path.abspath(root)

    #TODO: DO THIS PROPPERLY!!!!!!
    #environment = os.environ['CLUSTERONE_CLOUD']

    environment = os.environ.get('CLUSTERONE_CLOUD') or os.environ.get('TENSORPORT_CLOUD')
    environment = 'clusterone-cloud' if environment else "local"

    if environment == 'local':
        return os.path.join(root)
    elif environment == 'clusterone-cloud':
        return os.path.join('/logs/')
    else:
        print("Environment is not valid. Assuming local.")
        return os.path.join(root)

class ClusteroneClient(object):
    """
    Clusterone API Client
    ^^^^^^^^^^^^^^^^^^^^^

    Clusterone Client (just for short) is a simple Python module that is used to get most up_to_date API schema,
    and execute API calls.

    """
    username = ""
    api_schema = {}
    use_in_memory_schema = True
    git_token = ""


    #TODO: Test this!
    @lazy_property
    def framework_slugs(self):
        #TODO: Move this to function signature after removing 2.7 compliance
        # type: () -> [str]

        return [framework['slug'] for framework in self.get_frameworks()]

    #TODO: Test this!
    @lazy_property
    def instance_types_slugs(self):
        #TODO: Move this to function signature after removing 2.7 compliance
        # type: () -> [str]

        return [machine['slug'] for machine in self.get_instance_types() if machine['show_for_workers']]


    #TODO: Test this!
    @lazy_property
    def ps_type_slugs(self):
        #TODO: Move this to function signature after removing 2.7 compliance
        # type: () -> [str]

        return [machine['slug'] for machine in self.get_instance_types() if machine['show_for_ps']]

    @property
    def matrix_url(self):
        #type: () -> str
        # TODO: After removeing Python 2.7 compliance move to function signautre
        #TODO: TEST THIS!!!

        return self.api_url.replace('api', 'matrix')

    def __init__(self, token="", username="", environment='', use_in_memory_schema=True, schema_json_path=None,
            api_url=None):

        if not api_url:
            # TODO: Do something nasty here
            pass

        self.api_url = api_url

        # TODO replace this with proper url generator with urllib ASAP
        self.api_schema_url = "{}{}".format(api_url, "schema/")
        self.environment = environment
        self.use_in_memory_schema = use_in_memory_schema

        self.token = token
        self.username = username

        # Load Schema from file or given path
        if not use_in_memory_schema:
            if schema_json_path:
                self.document_path = schema_json_path
            else:
                self.document_path = py.path.local(
                    click.get_app_dir('clusterone')).join('schema.json')

        # Init CoreAPI Client
        self.transport = self.get_transport()
        self.decoders = [codecs.CoreJSONCodec(), codecs.JSONCodec(), codecs.DownloadCodec()]
        self.api_client = Client(
            transports=[self.transport], decoders=self.decoders)

        # Get Schema
        self.api_schema = self.download_schema()

        super(ClusteroneClient, self).__init__()

    def get_transport(self):
        """
        Creates HTTPTransport with auth header information
        :param token:
        :return: HTTPTransport
        """

        # This is a dirty, dirty hack - disabling SSL checks!!!
        # Remove this after fixing SSL on Roche!
        import requests
        from functools import partial

        class partialmethod(partial):
            def __get__(self, instance, owner):
                if instance is None:
                    return self

                return partial(self.func, instance, *(self.args or ()), **(self.keywords or {}))

        # This disables the SSL warnings that are raised on insecure connection
        import warnings

        try:
            from urllib3.exceptions import InsecureRequestWarning
            warnings.simplefilter('ignore', InsecureRequestWarning)
        except ImportError:
            # on some weird configuration the Urllib3 is not present
            # this is better than worrying the users and breaking CLI
            warnings.simplefilter('ignore', Warning)


        if self.token:
            if LOCAL_DEV:
                print('Using Token: %s************' % self.token[:4])
            auth = TokenAuthentication(token=self.token, scheme='JWT')
            _session = requests.Session()
            _session.send = partialmethod(_session.send, verify=False)
            #TODO: Fix this header passing!!!!!!!!
            return transports.HTTPTransport(headers={'Authorization': '%s %s' % ('JWT', self.token)}, session=_session)
        else:
            _session = requests.Session()
            _session.send = partialmethod(_session.send, verify=False)
            return transports.HTTPTransport(session=_session)

    def get_schema_json(self):
        """
        Reads API SCHEMA from memory or JSON document stored in Clusterone local path
        :return:
        """
        if self.api_schema and self.use_in_memory_schema:
            return self.api_schema

        else:
            if not self.document_path.ensure():
                print('Cannot read from schema JSON, please relogin')
                return None
            store = self.document_path.open('rb')
            content = store.read()
            store.close()
            codec = codecs.CoreJSONCodec()
            return codec.load(content)

    def set_schema(self, document):
        """
        Creates Schema JSON in Clusterone local path
        :param document:
        :return:
        """
        codec = codecs.CoreJSONCodec()
        content = codec.dump(document)
        store = self.document_path.open('wb')
        store.write(content)
        store.close()
        print('Saved schema JSON')

    def download_schema(self):
        """
        Uses Basic Auth to get Schema JSON and save it
        :param document:
        :return:
        """
        API_SCHEMA = self.api_schema_url

        if LOCAL_DEV:
            print('Loading Clusterone API Schema: %s' % API_SCHEMA)
        try:
            api_schema = self.api_client.get(API_SCHEMA)

            if self.use_in_memory_schema:
                self.api_schema = api_schema
            else:
                self.set_schema(api_schema)

            return api_schema

        except coreapi.exceptions.ErrorMessage as e:
            # Reset token and try again
            # TODO this produces a nasty loop - will make hundrets of requests currently. Reset client triggers download schema...
            self.reset_client()
            api_schema = self.api_client.get(API_SCHEMA)

            if self.use_in_memory_schema:
                self.api_schema = api_schema
            else:
                self.set_schema(api_schema)

            return api_schema

        except Exception as e:
            print('Cannot download API Schema: %s' % str(e))
            raise

    def client_action(self, actions_keys, params=None, validate=True):
        """
        Wrapper for Client.action that set decoders, transports and schema document
        :param token:
        :param actions_keys:
        :param schema:
        :param params:
        :param validate:
        :return:
        """
        try:
            data = self.api_client.action(
                self.api_schema, actions_keys, params=params, validate=validate)
            if LOCAL_DEV:
                print("Success: %s" % data)
            return data
        except coreapi.exceptions.LinkLookupError as exc:
            raise client_exceptions.LoginNotSupplied()
        except coreapi.exceptions.ErrorMessage as exc:
            #TODO: Throtling, server error, gateway timeout, maintanance mode
            # Handle S3 Bucket name
            if hasattr(exc, 'error') and "S3 Bucket" in exc.error._data.get('messages', [''])[0]:
                raise client_exceptions.BucketNameNotAvaliable()
            if 'non_field_errors' in exc.error and exc.error['non_field_errors']:
                if (exc.error.title == '400 Bad Request') and exc.error._data['non_field_errors']._data[0] == 'Unable to log in with provided credentials.':
                    raise client_exceptions.LoginFailed()
            else:
                # TODO refactor the hell out of this
                if "400" in exc.error._title:
                    if "Enter a valid \"slug\" consisting of letters, numbers, underscores or hyphens." in exc.error._data.get("display_name", [''])[0]:
                        raise client_exceptions.InvalidProjectName()
                    elif "Project name is not unique" in exc.error._data.get("display_name", [''])[0]:
                        raise client_exceptions.DuplicateProjectName()
                    else:
                        raise
                if "403" in exc.error._title and 'You do not have enough resources to start' in exc.error._data['detail']:
                    raise client_exceptions.InsufficientResources()
                if "500" in exc.error._title:
                    raise client_exceptions.InternalServiceError()

                else:
                    if "404" not in exc.error._title:
                        print("API Error: %s" % exc.error)
                    else:
                        raise exc

    def reset_client(self):
        #TODO: Move this to function signature after removing 2.7 compliance
        # type: () -> None
        """
        Used to reset token, schema and set empty transrport method for client.
        Fixing CLUS-82.
        """

        self.token = None
        self.transport = self.get_transport()
        self.api_client = Client(
            transports=[self.transport], decoders=self.decoders)

        #TODO: Change to aquire schema in the future - to take advantage of cached schema and not making request
        self.api_schema = self.download_schema()

    # -----------------------------
    # Authentication
    def api_login(self, username, password):
            if LOCAL_DEV:
                print('Loading Initial Clusterone API Schema: %s' %
                      self.api_schema_url)

            # Login to get token
            response = self.client_action(actions_keys=['token', 'create'], params={
                'username': username,
                'password': password,
            }, validate=True)
            # Reset Token and transport headers
            if not response:
                message = "Couldn't login, please check your username and password"
                return None, message

            self.token = response.get('token')
            self.transport = self.get_transport()
            self.api_client = Client(
                transports=[self.transport], decoders=self.decoders)
            self.api_schema = self.download_schema()

            # Verify
            profile_response = self.client_action(actions_keys=['profile', 'list'], params={
            }, validate=True)

            self.git_token = profile_response.get('git_token')
            self.username = username

            return self.token

    def create_dataset(self, display_name, source='gitlab', description='Clusterone Dataset'):
        """
        Creates a dataset thru API
        :return: Dataset Unique Name
        """
        try:
            response = self.client_action(['datasets', 'owned', 'create'], params={
                'display_name': display_name,
                'description': description,
                'source': source,
                'parameters': {}
            }, validate=True)

            return response

        except client_exceptions.InvalidProjectName as exception:
            raise client_exceptions.InvalidDatasetName()
        except client_exceptions.DuplicateProjectName as exception:
            raise client_exceptions.DuplicateDatasetName()
        except client_exceptions.UnsupportedSource as exception:
            raise client_exceptions.UnsupportedSource()
        except client_exceptions.BucketNameNotAvaliable as exception:
            raise client_exceptions.BucketNameNotAvaliable()

    def create_project(self, display_name, description='Clusterone Project'):
        """
        Creates a project thru API
        :return: Project Unique Name
        """

        # Add Github support
        try:
            response = self.client_action(['projects', 'owned', 'create'], params={
                'display_name': display_name,
                'description': description,
                'parameters': {}
            }, validate=True)

            return response.get('name')

        #TODO: Somehow redo this -> catching all exceptions bloats sentry and causes further development problems
        #TODO: If this is the final Exception catcher then it shall: log to Sentry then kill the process
        except Exception as exception:
                if isinstance(exception, client_exceptions.InvalidProjectName):
                    raise client_exceptions.InvalidProjectName()
                elif isinstance(exception, client_exceptions.DuplicateProjectName):
                    raise client_exceptions.DuplicateProjectName()
                else:
                    print("Couldn't create a project thru API, error: %s" % str(exception))

                    return False

    def get_project(self, name, username=None):
        """
        Get Project from Repo
        :return: Project JSON
        """
        try:
            response = self.client_action(['projects', 'details', 'read'], params={
                'name': name,
                'username': username
            }, validate=False)
            return response
        except Exception as e:
            #TODO: This is crap, redo this ASAP
            if isinstance(e, client_exceptions.LoginNotSupplied):
                raise e
            if "404" in e.error._title:
                raise client_exceptions.NonExistantProject()
            else:
                print("Couldn't fetch a project, error: %s" % str(e))

                return False

    def get_projects(self, owner=None, writer=None, reader=None):
        """
        Get List of Owned Projects
        :return: List of Project JSONs
        """
        if owner:
            action = 'owned'
        elif writer:
            action = 'writable'
        elif reader:
            action = 'readable'
        else:
            action = 'readable'

        try:
            response = self.client_action(
                ['projects', action, 'list'], params={}, validate=False)
            return response
        except Exception as e:
            print("Couldn't fetch a project, error: %s" % str(e))

            return False

    def delete_project(self, name, username):
        """
        Deletes a Project
        :return:
        """
        try:
            response = self.client_action(['projects', 'details', 'delete'], params={
                'name': name,
                'username': username
            }, validate=True)
            return response
        except Exception as e:
            print("Couldn't delete a project, error: %s" % str(e))

            return False

    def delete_dataset(self, name, username):
        """
        Deletes a dataset
        :return:
        """
        # TODO: fix this
        try:
            response = self.client_action(['datasets', 'details', 'delete'], params={
                'name': name,
                'username': username
            }, validate=True)
            return response
        except Exception as e:
            print("Couldn't delete a dataset, error: %s" % str(e))

            return False

    def get_dataset(self, name, username):
        """
        Get Datasets from Repo
        :return: Project JSON
        """
        try:
            response = self.client_action(['datasets', 'details', 'read'], params={
                'name': name,
                'username': username
            }, validate=False)
            return response
        except Exception as e:
            if "404" in e.error._title:
                raise client_exceptions.NonExistantDataset()
            else:
                print("Couldn't fetch a dataset, error: %s" % str(e))

                return False

    def get_datasets(self, owner=None, reader=None, writer=None):
        """
        Get List of Owned Datasets
        :return: List of Project JSONs
        """
        # TODO: add various ownership levels
        try:
            if owner is not None:
                response = self.client_action(['datasets', 'owned', 'list'], params={
                }, validate=False)
            else:
                response = self.client_action(['datasets', 'list'], params={
                }, validate=False)
            return response
        except Exception as e:
            print("Couldn't fetch a datasets, error: %s" % str(e))

            return False

    def get_events(self):
        """
        Get List of user related events
        :return: List of Jobs JSONs
        """
        # TODO: add various ownership levels
        # TODO: what can this return? - discuss with Michał -> potencial edge cases
        # Error message: "Failed to query recent events. Perhaps you have not started a job yet. Try 'just run'."
        response = self.client_action(
            ['events', 'list'], params={}, validate=False)
        return response

    def create_event(self, job_id, event_type, event_level=20, event_content=None):
        """
        Create Event
        :return:
        """
        try:
            response = self.client_action(['events', 'create'], params={
                'job': job_id,
                'event_type': event_type,
                'event_level': event_level,
                'event_content': {}
            }, validate=True)
            return response
        except Exception as e:
            print("Couldn't create event, error: %s" % str(e))

            return False

    @lru_cache(maxsize=1)
    def get_instance_types(self, params=None):
        """
        Get List of Instance Types
        :return: List of AWS Instance Types JSONs
        """
        try:
            response = self.client_action(
                ['instance-types', 'list'], params=params, validate=False)
            return response.get('results')
        except Exception as e:

            print("Couldn't fetch list of instances, error: %s" % str(e))

    @lru_cache(maxsize=1)
    def get_frameworks(self, params=None):
        #TODO: What is a list with slug, name, number? A dict? A list of lists?
        """
        Get List of ML frameworks
        :return: List of frameworks with slug, name and number
        """
        try:
            response = self.client_action(
                ['frameworks', 'list'], params=params, validate=False)
            return response.get('results')
        #TODO: WHY LEO, WHY?!!!!!!!
        except Exception as e:

            print("Couldn't fetch list of frameworks, error: %s" % str(e))

    def get_tf_versions(self, params=None):
        """
        DEPRACATED - use get_frameworks instead
        :return: List of frameworks with slug, name and number
        """
        return self.get_frameworks(params)

    def get_jobs(self, params=None):
        """
        Get List of User Running Jobs
        :return: List of Jobs JSONs
        """
        try:
            if params:
                params.update({'limit': 200})
            else:
                params = {'limit': 200}
            response = self.client_action(
                ['jobs', 'list'], params=params, validate=False)
            return response
        except Exception as e:
            print("Couldn't fetch a project, error: %s" % str(e))

            return False

    def get_job(self, params=None):
        """
        Get a single Job
        :return: Job JSONs
        """
        try:
            response = self.client_action(
                ['jobs', 'read'], params=params, validate=False)
            return response
        except Exception as e:
            print("Couldn't fetch a job, error: %s" % str(e))

            return False

    def create_job(self, name, description=None, parameters=None):
        """
        create a Job, require repository ID
        :return:
        """
        request_parameters = self._prepare_request_parameters(name, description, parameters)

        try:
            response = self.client_action(['jobs', 'create'], params=request_parameters, validate=True)

            return response
        except Exception as e:
            try:
                error_message = e.error._data['parameters']['workers']['non_field_errors'][0]
                if "Wrong number of GPUs." in error_message:
                    raise WrongNumberOfGPUs(error_message)
            except (AttributeError, KeyError):
                pass
            try:
                if 'No commits found in the project repository.' in e.error._data['messages']:
                    raise NoCommitsInProjectFound()
            except (AttributeError, KeyError):
                pass

            print("Couldn't create a job, error: %s" % str(e))

            raise

    @classmethod
    def _prepare_request_parameters(cls, name, description, parameters):
        request_parameters = {}

        # if parameter not provided, it should not be sent to the API
        if parameters['datasets_set'] is not None:
            request_parameters['datasets_set'] = parameters['datasets_set']

        if parameters['git_commit_hash'] is not None:
            request_parameters['git_commit_hash'] = parameters['git_commit_hash']

        request_parameters['repository'] = parameters.pop('repository')
        request_parameters['display_name'] = name
        request_parameters['description'] = description
        request_parameters['parameters'] = parameters
        return request_parameters

    @staticmethod
    def _pop_from_source_to_target_if_exists(source, target, key):
        """If key exists in source (parameters) dict - move the key:value to target (request_parameters) dict"""
        try:
            value = source.pop(key)
            target[key] = value
        except KeyError:
            pass

    def delete_job(self, job_id):
        """
        Deletes a Job
        :return:
        """
        response = self.client_action(['jobs', 'delete'], params={
            'job_id': job_id,
        }, validate=True)
        return response

    def start_job(self, job_id):
        """
        Starts a Job
        :return:
        """
        try:
            response = self.client_action(['jobs', 'start'], params={
                'job_id': job_id,
            }, validate=True)
            return response
        except client_exceptions.InsufficientResources as exception:
            raise exception
        except Exception as exception:
            if "404" in exception.error._title:
                raise client_exceptions._NonExistantJob()

            print("Couldn't start a job, error: %s" % str(exception))

            return False

    def stop_job(self, job_id):
        """
        Stops a Job
        :return:
        """
        try:
            response = self.client_action(['jobs', 'stop'], params={
                'job_id': job_id,
            }, validate=True)
            return response
        except Exception as e:
            print("Couldn't stop a job, error: %s" % str(e))

            return False

    def get_file_list(self, job_id):
        """
        Get list of files/outputs
        :return:
        """
        try:
            response = self.client_action(['jobs', 'files', 'list'], params={
                'job_id': job_id,
            }, validate=True)
            if len(response) > 0:
                file_list = response[0]['contents']
                return file_list
            else:
                return []
        except Exception as e:
            print("Couldn't find a job or files, error: %s" % str(e))
            return False

    def download_file(self, job_id, filename):
        """
        Download file for Job
        :return:
        """
        try:

            download = self.client_action(['jobs', 'file', 'read'], params={
                'job_id': job_id,
                'filename': filename,
            }, validate=False)
            return download
        except Exception as e:
            print("Download file %s error: %s" % (filename, str(e)))

            return False
