import logging
from os import environ
from datetime import datetime

from .runner import run
from .getting_started_scenario import GettingStarted

LOG_PATH = "./logs"
LOG_FILENAME = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-UTC")


log_path = "{0}/{1}.log".format(LOG_PATH, LOG_FILENAME)
log_formatter = logging.Formatter("%(asctime)s: [%(levelname)s] %(message)s", datefmt='%m/%d/%Y %H:%M:%S')

file_handler = logging.FileHandler(log_path)
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

the_logger = logging.getLogger()
the_logger.setLevel(logging.DEBUG)
the_logger.addHandler(file_handler)
the_logger.addHandler(console_handler)

logging.info("Logger init, saving to path: {}".format(log_path))

run(GettingStarted)
