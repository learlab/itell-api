import atexit
import logging
import logging.config
import logging.handlers
from multiprocessing import Queue  # in case we start using multiprocessing

from .json_logger import JSONFormatter


def setup_logging():
    simple_formatter = logging.Formatter(
        fmt="[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    json_formatter = JSONFormatter(
        fmt_keys={
            "level": "levelname",
            "message": "message",
            "timestamp": "asctime",
            "logger": "name",
            "module": "module",
            "function": "funcName",
            "line": "lineno",
            "thread": "threadName",
        }
    )

    # Define the handlers
    stderr_handler = logging.StreamHandler()
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(simple_formatter)

    file_json_handler = logging.handlers.RotatingFileHandler(
        filename="logs/my_app.log.jsonl",
        maxBytes=1_000_000,  # 1MB
        backupCount=3,
    )
    file_json_handler.setLevel(logging.INFO)
    file_json_handler.setFormatter(json_formatter)

    # Set up the queue and the queue handler
    queue = logging.handlers.QueueHandler(queue=Queue())
    queue_handler = logging.handlers.QueueHandler(queue)
    queue_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(queue_handler)

    listener = logging.handlers.QueueListener(
        queue, stderr_handler, file_json_handler, respect_handler_level=True
    )
    listener.start()
    atexit.register(listener.stop)
