import os
import time
import logging
import logging.config

logger = logging.getLogger(__name__)
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "%(asctime)s.%(msecs)03d   "
                "%(levelname)11s: %(message)s [%(name)s:%(lineno)d]"
            ),
            "datefmt": '%Y.%m.%d %H:%M:%S'

        },
        "simple": {
            "format": "%(levelname)-11s - %(message)s [%(name)s:%(lineno)d]",
            "datefmt": "%Y.%m.%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "formatter": "simple",
            "class": "logging.StreamHandler",
        },
        "debug": {
            "level": "INFO",
            "formatter": "verbose",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "",
            "mode": "a",
            "maxBytes": 104857600,
            "backupCount": 5,
        }
    },
    "root": {}
}


def configure_logging(application, project_dir, debug):
    """Configure the logging for the current application.

    Also if the production environment configuration exists the logging
    directory will be assumed to be ``/data/log/${application}`` and if not
     then the ``${cwd}/log`` directory will be used. The logging directory will
    be created if it does not already exists.

    :param str application: Application name used to determine where the
        logging configuration file and logging directory are
    :type application: str
    :param project_dir: Project dir path.
    :type project_dir: str
    :param debug: Information if debug mode is enabled
    :type debug: bool
    """
    # Get the log directory
    log_dir = (
        '/data/log/{0}'.format(application) if not debug
        else os.path.join(project_dir, 'log')
    )
    debug_log = os.path.join(log_dir, '{0}.log'.format(application))

    if debug:
        LOGGING_CONFIG["root"] = {
            "handlers": ["debug", "console"],
            "level": "DEBUG",
            "propagate": 0
        }
    else:
        LOGGING_CONFIG["root"] = {
            "handlers": ["debug"],
            "level": "DEBUG",
            "propagate": 0
        }

    for key, handler in LOGGING_CONFIG["handlers"].items():
        if key == 'debug':
            handler['filename'] = debug_log

    logging.Formatter.converter = time.gmtime
    # Configure logging
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info(
        'Logging configured for application {}. Log: {}'.format(
            application, debug_log
        )
    )
