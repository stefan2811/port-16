"""Module for server error handler definitions"""

from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request, responses, status


async def generic_error_handler(_: Request, e: Exception) -> JSONResponse:
    """
    Default Exception error handler

    :param _: Request object
    :param e: Exception object
    :return: Error response
    """
    return responses.JSONResponse(
        content={
            'type': 'generic.server_error',
            'title': 'An unhandled exception raised',
            'detail': str(e),
            'instance': None,
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


async def http_error_handler(_: Request, e: HTTPException) -> JSONResponse:
    """
    Default HTTPException error handler

    :param _: Request object
    :param e: Exception object
    :return: Error response
    """
    return JSONResponse(
        content={
            'type': 'generic.http_exception',
            'title': 'Generic http exception raised',
            'detail': e.detail,
            'instance': None,
        },
        status_code=e.status_code
    )
