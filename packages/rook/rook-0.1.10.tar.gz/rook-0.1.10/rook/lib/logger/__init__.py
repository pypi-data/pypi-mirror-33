import json

import os
import platform

if "rook" in __name__:
    # This is caused by not changing sys.path in Rook combined with the way we package the code
    from rook.interfaces.config import LoggingConfiguration
else:
    from interfaces.config import LoggingConfiguration

from .logger_factory import LoggerFactory
from .logging_types import LogType
from .kw_log import KWLogger


def logger_with_metadata(*extra_tags):
    return KWLogger(_base_logger, list(extra_tags))


def _build_logger():
    import sys
    if "unittest" in sys.argv[0]:
        log_level = 10
        LoggingConfiguration.LOG_TO_STDERR = True
    else:
        log_level = LoggingConfiguration.LOG_LEVEL
    if os.environ.get("LOCAL_LOGGING", platform.system() == "Darwin" or platform.system() == "Windows"):  # SUPER NAIVE
        LoggingConfiguration.LOG_TO_STDERR = True
        LoggingConfiguration.LOG_TO_REMOTE = False
    return LoggerFactory(
        LoggingConfiguration.LOGGER_NAME,
        log_level,
        LoggingConfiguration.FILE_NAME,
        LoggingConfiguration.LOG_TO_STDERR,
        LoggingConfiguration.LOG_TO_REMOTE,
        LoggingConfiguration.PROPAGATE_LOGS
    ).get_logger()


logger_parmas = dict(
    name=LoggingConfiguration.LOGGER_NAME,
    log_level=LoggingConfiguration.LOG_LEVEL,
    file_name=LoggingConfiguration.FILE_NAME,
    stderr=LoggingConfiguration.LOG_TO_STDERR,
    log_to_remote=LoggingConfiguration.LOG_TO_REMOTE,
    propagate_logs=LoggingConfiguration.PROPAGATE_LOGS)
_base_logger = _build_logger()
logger = KWLogger(_base_logger)
logger.info("Initialized logger")
logger.info("Logger params: {}".format(json.dumps(logger_parmas)))
