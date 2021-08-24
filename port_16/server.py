"""Server configuration module. Routes, middlewares and exception handlers are
defined here.
"""
from fastapi import FastAPI, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

from port_16.api.status.handlers import status
from port_16.errors import (
    generic_error_handler,
    http_error_handler,
)


def attach_routes(app: FastAPI) -> None:
    """Attach routes to app
    :param app: App object
    """
    app.include_router(
        prefix='/status',
        tags=['port-16'],
        router=status.router
    )


def attach_error_handlers(app: FastAPI) -> None:
    """Attach error handlers to app. Error handlers handle specific errors
    thrown by route handlers.
    :param app: App object
    """
    app.add_exception_handler(Exception, generic_error_handler)
    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
