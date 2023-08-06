from collections import namedtuple
from enum import Enum


class Output(Enum):
    NONE = 0
    ANY = 1
    CHECKPOINT = 2
    LOSS = 3


UserCredentials = namedtuple("UserCredentials", "username password email")
