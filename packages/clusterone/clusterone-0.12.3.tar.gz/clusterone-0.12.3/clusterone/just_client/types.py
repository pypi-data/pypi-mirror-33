from enum import Enum


class TaskStatus(Enum):
    """
    Task == Job & Notebook
    """

    created = "created"
    started = "started"
    stopped = "stopped"
