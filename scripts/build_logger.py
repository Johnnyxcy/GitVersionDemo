import logging
import sys

import typing


class _BuildLoggerFormatter(logging.Formatter):
    grey = '\x1b[38;20m'
    light_green = '\x1b[92;20m'
    yellow = '\x1b[33;20m'
    red = '\x1b[31;20m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'
    format = '[%(levelname)s][%(asctime)s] %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: light_green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger: typing.Final[logging.Logger] = logging.getLogger("Builder")
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
_console_handler = logging.StreamHandler(stream=sys.stdout)
_console_handler.setLevel(logging.DEBUG)

_console_handler.setFormatter(_BuildLoggerFormatter())

logger.addHandler(_console_handler)
