class ClusteroneException(Exception):
    def __init__(self):
        super(ClusteroneException, self).__init__()
        self.exit_code = 1


class InvalidProjectName(ClusteroneException):
    def __str__(self):
        return "Your project name is invalid, please be sure to only use letters, digits, hyphens, and underscores."


class InvalidDatasetName(ClusteroneException):
    def __str__(self):
        return "Your dataset name is invalid, please be sure to only use letters, digits, hyphens, and underscores."


class DuplicateProjectName(ClusteroneException):
    def __str__(self):
        return "Duplicate project name. Project names must be unique."


class DuplicateNotebookName(ClusteroneException):
    def __str__(self):
        return "Duplicate notebook name. Notebook names must be unique."


class UnsupportedSource(ClusteroneException):
    def __str__(self):
        return "Unsupported dataset source."

class BucketNameNotAvaliable(ClusteroneException):
    def __str__(self):
        return "The requested bucket name is not available. The bucket namespace is shared by all users of the system."

class DuplicateDatasetName(ClusteroneException):
    def __str__(self):
        return "Duplicate dataset name. Dataset names must be unique."


class LocalRepositoryFailure(ClusteroneException):
    def __str__(self):
        return "Couldn't find a Git repository. Please run this command in a valid repository or provide a valid repository path."


class RemoteAquisitionFailure(ClusteroneException):
    def __str__(self):
        return "Failed to get Git remote. Please contact Clusterone for support."


class LinkAlreadyPresent(ClusteroneException):
    def __str__(self):
        return "Cannot link. This repository already has a Clusterone remote."


class NonExistantProject(ClusteroneException):
    def __str__(self):
        return "Cannot resolve name to a project. Are you sure that such a project exists? If so, consider checking project owner and your permissions."


class NonExistantDataset(ClusteroneException):
    def __str__(self):
        return "Cannot resolve name to a dataset. Are you sure that such a dataset exists? If so, consider checking dataset owner and your permissions."


class JobNameConflict(ClusteroneException):
    def __init__(self, possible_ids):
        super(JobNameConflict, self).__init__()
        self.ids = possible_ids

    def __str__(self):
        return "{}{}{}".format(
            "Job name resolves to multiple IDs:\n",
            "".join(["{}\n".format(id) for id in self.ids]),
            "Cannot proceed. Please rerun this command with one of the IDs above.")


class _NonExistantJob(ClusteroneException):
    def __str__(self):
        return "There is no job with such ID. Are you sure that such a job exists?"


class NonExistantJob(ClusteroneException):
    def __str__(self):
        return "Cannot resolve name to a job. Are you sure that such a job exists?"


class _NonExistantNotebook(ClusteroneException):
    def __str__(self):
        return "There is no notebook with such ID. Are you sure that such a notebook exists?"


class NonExistantNotebook(ClusteroneException):
    def __str__(self):
        return "Cannot resolve name to a notebook. Are you sure that such a notebook exists?"


# TODO: Is this the most approperiate? See usage in tp_client
class LoginNotSupplied(ClusteroneException):
    def __str__(self):
        return "Action not authorized. Please log in or check your token."


class InternalServiceError(ClusteroneException):
    def __str__(self):
        return "Something went terribly wrong on our side, please contact us for immediate support."


class SoftInternalServiceError(ClusteroneException):
    """
    This is to be used in case of unknown problem if it may be resolved by logout-login action by the user.
    """

    def __str__(self):
        return "Something went wrong on our side. Could you please logout the login again? If the problem persits please contact us for immediate support."


class RunningJobRemoveAttempt(ClusteroneException):
    def __str__(self):
        return "This job is currently running."


class BusyProjectRemoveAttempt(ClusteroneException):
    def __str__(self):
        return "This project has currently running jobs."


class InsufficientResources(ClusteroneException):
    def __str__(self):
        return "You are exceeding you plan limit or do not have enough credits to proceed."


class BusyDatasetRemoveAttempt(ClusteroneException):
    def __str__(self):
        return "This dataset is currently in use by a running job. Removing it may cause the job to fail."


class NotSupported(ClusteroneException):
    def __str__(self):
        return "This CLI version is not up to date. Please run `pip install clusterone --upgrade`."


class LoginFailed(ClusteroneException):
    def __str__(self):
        return "Couldn't login, invalid username or password."


class NoCommitsInProjectFound(ClusteroneException):
    def __str__(self):
        return 'No commits found in the project repository.'
