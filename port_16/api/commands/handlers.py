from typing import Dict, Any

from fastapi import APIRouter, BackgroundTasks

from ..charge_point.schemas import ChargingPointModel
from .schemas import (
    AuthorizeResponse, AuthorizeRequest,
    StartTransaction, StopTransaction
)
from .operations import (
    execute_boot_notification, execute_heartbeat, execute_authorize,
    execute_start_transaction, execute_stop_transaction
)

router = APIRouter()


@router.post(
    path='/{cp_id}/commands/boot-notification',
    response_model=ChargingPointModel,
    summary='Executes boot notification command',
    description='Uses provided charging point id and executes command',
    response_description='Charging point data',
)
async def boot_notification_command(cp_id: str) -> Dict[str, Any]:
    """
    Executes boot notification command for charging point id.

    :param cp_id: Id of ChargingPoint for which command will be executed.
    :return: Charging point data.
    """
    return await execute_boot_notification(cp_id)


@router.post(
    path='/{cp_id}/commands/heartbeat',
    response_model=ChargingPointModel,
    summary='Executes heartbeat command',
    description='Uses provided charging point id and executes command',
    response_description='Charging point data',
)
async def heartbeat_command(
    cp_id: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Executes boot notification command for charging point id.

    :param cp_id: Id of ChargingPoint for which command will be executed.
    :param background_tasks: FastAPI tool which will be used for starting
        heartbeat function in background.
    :return: Charging point data.
    """
    return await execute_heartbeat(cp_id, background_tasks)


@router.post(
    path='/{cp_id}/commands/authorize',
    response_model=AuthorizeResponse,
    summary='Executes authorize command',
    description='Uses provided charging point id and executes command',
    response_description='Authorize response',
)
async def authorize_command(
    cp_id: str,
    auth_request: AuthorizeRequest
) -> Dict[str, Any]:
    """
    Executes authorize command for charging point id.

    :param cp_id: Id of ChargingPoint for which command will be executed.
    :param auth_request: Id of tag in request which will be authorized.
    :return: Authorize response
    """
    return await execute_authorize(cp_id, auth_request.id_tag)


@router.post(
    path='/{cp_id}/commands/start-transaction',
    response_model=AuthorizeResponse,
    summary='Executes start transaction command',
    description='Uses provided charging point id and executes command',
    response_description='Authorize response',
)
async def start_transaction_command(
    cp_id: str,
    transaction: StartTransaction
) -> Dict[str, Any]:
    """
    Executes start transaction command for charging point id.

    :param cp_id: Id of ChargingPoint for which command will be executed.
    :param transaction: Start transaction request data.
    :return: Authorize response
    """
    return await execute_start_transaction(cp_id, transaction)


@router.post(
    path='/{cp_id}/commands/stop-transaction',
    response_model=AuthorizeResponse,
    summary='Executes stop transaction command',
    description='Uses provided charging point id and executes command',
    response_description='Authorize response',
)
async def stop_transaction_command(
    cp_id: str,
    transaction: StopTransaction
) -> Dict[str, Any]:
    """
    Executes stop transaction command for charging point id.

    :param cp_id: Id of ChargingPoint for which command will be executed.
    :param transaction: Stop transaction request data.
    :return: Authorize response
    """
    return await execute_stop_transaction(cp_id, transaction)
