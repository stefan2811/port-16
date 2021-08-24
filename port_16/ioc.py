"""Module for dependency injection configuration"""

import os
import logging
from pathlib import Path

from inject import Binder

from port_16.logs import configure_logging

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def production(binder: Binder) -> None:
    """Injector configuration"""
    # Bind project path
    project_dir = Path(__file__).parents[1]
    binder.bind('project_dir', project_dir)

    # Configure logging
    configure_logging('port-16', BASE_DIR, True)

    logger = logging.getLogger(__name__)
    logger.info('Starting app..')
