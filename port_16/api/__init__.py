from fastapi import FastAPI

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
        prefix='/charging-points',
        tags=['commands'],
        router=commands_handlers.router
    )
