from fastapi import FastAPI

from .commands.handlers import misc
from .commands.handlers import authorize
from .commands.handlers import transaction
from .charge_point import handlers as cp_handlers

from .commands import handlers as commands_handlers


def attach_cp_routes(app: FastAPI) -> None:
    """
    Attach charge point and commands routes to app
    :param app: App object
    """
    app.include_router(
        prefix='/charging-points',
        tags=['charging-point'],
        router=cp_handlers.router
    )
    app.include_router(
        prefix='/commands',
        tags=['misc-commands'],
        router=misc.router
    )
    app.include_router(
        prefix='/commands',
        tags=['transaction-commands'],
        router=transaction.router
    )
    app.include_router(
        prefix='/commands',
        tags=['authorize-commands'],
        router=authorize.router
    )
