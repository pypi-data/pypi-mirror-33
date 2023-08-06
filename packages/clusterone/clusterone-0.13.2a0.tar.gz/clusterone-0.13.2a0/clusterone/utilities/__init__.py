from .main import random_job_name
from .main import silent_prompt
from .log_err import log_error

from .path_to import path_to_project
from .path_to import path_to_job_id
from .path_to import path_to_dataset

from .time_limit_to_minutes import main as time_limit_to_minutes
from .make_table import main as make_table
from .job_serializer import main as serialize_job

from .choice import Choice, lazy_property, lazify

from .version import is_latest_version

from .docstring import append_to_docstring
