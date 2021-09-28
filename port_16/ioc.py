"""Module for dependency injection configuration"""

import os
import logging
from pathlib import Path
from typing import Dict, Callable

from inject import Binder

from port_16.logs import configure_logging

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP_NAME = 'port-16'


def production(
    instance_kwargs: Dict,
    provider_kwargs: Dict
) -> Callable:
    """
    Injector configuration
    """
    def bind_configuration(binder: Binder):
        # Bind project path
        project_dir = Path(__file__).parents[1]
        binder.bind('project_dir', project_dir)

        for key, value in instance_kwargs.items():
            binder.bind(key, value)

        for key, value in provider_kwargs.items():
            binder.bind_to_provider(key, value)

        # Configure logging
        configure_logging(APP_NAME, BASE_DIR, True)

        logger = logging.getLogger(__name__)
        logger.info(f'Starting app {APP_NAME}..')

    return bind_configuration
