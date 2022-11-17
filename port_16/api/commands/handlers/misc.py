from typing import Dict, Any

from fastapi import APIRouter, BackgroundTasks

from ...charge_point.schemas import ChargingPointModel
from ..operations import (
    execute_boot_notification, execute_heartbeat
)

router = APIRouter()


@router.post(
    path='/{cp_id}/boot-notification',
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
    path='/{cp_id}/heartbeat',
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
