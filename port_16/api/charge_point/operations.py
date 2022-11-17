import logging
from typing import Dict, Any

from fastapi import BackgroundTasks

from port_16.api.charge_point.schemas import ChargingPointModel
from port_16.api.common import cp_db, start_cp, ChargePointService

logger = logging.getLogger(__name__)


async def create_charging_point(
    create_model: ChargingPointModel,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Creates and starts ChargingPoint using provided data and background_tasks
    tool. Returns ChargingPoint data.

    :param create_model: ChargingPointModel which will be used for starting.
    :param background_tasks: FastApi tool which will be used for starting
        background task which listens websocket.
    :return: Created ChargingPoint data.
    """
    cp_db.validate_cp_already_created(create_model.identity)
    service = ChargePointService(create_model.identity)
    await service.store_entity(create_model)
    background_tasks.add_task(start_cp, create_model)
    return create_model.dict()


async def get_charging_point(
    cp_id: str,
) -> Dict[str, Any]:
    """
    Gets and returns ChargingPoint data with provided id. If ChargingPoint is
    not found in system proper exception will be raised.

    :param cp_id: Id of ChargingPoint.
    :return: ChargingPoint data.
    """
    cp = cp_db.validate_and_get(cp_id, command='Get charging point')
    cp_model = await cp.cp_service.validate_get_entity()
    return cp_model.dict()


async def delete_charging_point(
    cp_id: str,
) -> Dict[str, Any]:
    """
    Deletes charging point from system with provided id.

    :param cp_id: Id of ChargingPoint.
    :return: ChargingPoint data.
    """
    cp = cp_db.validate_and_get(cp_id, command='Delete charging point')
    cp_model = await cp.cp_service.validate_get_entity()
    await cp.close_connection()
    cp_db.remove_cp(cp_id)
    await cp.cp_service.delete_storage_entity()
    return cp_model.dict()


async def start_charging_point(
    cp_id: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Queries and starts ChargingPoint using provided cp_id and background_tasks
    tool. Returns ChargingPoint data.

    :param cp_id: Id of ChargingPointModel which will be used for starting.
    :param background_tasks: FastApi tool which will be used for starting
        background task which listens websocket.
    :return: Created ChargingPoint data.
    """
    service = ChargePointService(cp_id)
    cp_model = await service.validate_get_entity()
    background_tasks.add_task(start_cp, cp_model)
    return cp_model.dict()
