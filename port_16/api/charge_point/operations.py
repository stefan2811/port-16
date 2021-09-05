import logging
from typing import Dict, Any

from fastapi import BackgroundTasks
from fastapi.exceptions import HTTPException

from port_16.api.charge_point import cp_db
from port_16.api.charge_point.schemas import ChargingPointModel
from port_16.api.charge_point.service import heartbeat, start_cp

logger = logging.getLogger(__name__)


def create_charging_point(
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
    cp_id = create_model.identity
    cp = cp_db.get_cp(cp_id)
    if cp is not None:
        logger.warning(
            'Charging point with provided id: '
            '{} already created in system'.format(cp_id)
        )
        raise HTTPException(
            status_code=409,
            detail=f'Charging point with id {cp_id} already created in system'
        )

    background_tasks.add_task(start_cp, create_model)
    return create_model.dict()


def get_charging_point(
    cp_id: str,
) -> Dict[str, Any]:
    """
    Gets and returns ChargingPoint data with provided id. If ChargingPoint is
    not found in system proper exception will be raised.

    :param cp_id: Id of ChargingPoint.
    :return: ChargingPoint data.
    """
    cp = cp_db.get_cp(cp_id)
    if cp is None:
        logger.warning(
            'Charging point not found with provided id: {}'.format(cp_id)
        )
        raise HTTPException(
            status_code=404,
            detail=f'Charging point with id {cp_id} not found in system'
        )

    return cp.cp_data.dict()


def delete_charging_point(
    cp_id: str,
) -> Dict[str, Any]:
    cp = cp_db.get_cp(cp_id)
    if cp is None:
        logger.warning(
            'Charging point not found with provided id: {}'.format(cp_id)
        )
        raise HTTPException(
            status_code=404,
            detail=f'Charging point with id {cp_id} not found in system'
        )

    cp_db.remove_cp(cp_id)
    return cp.cp_data.dict()


async def execute_boot_notification(cp_id: str) -> Dict[str, Any]:
    """
    Executes boot notification command for provided ChargingPoint id.

    :param cp_id: Id of CP for which command will be executed.
    """
    cp = cp_db.get_cp(cp_id)
    if cp is None:
        logger.warning(
            "Could not find charging point data with id: {}."
            "Boot notification command will be stopped.".format(cp_id)
        )
        raise HTTPException(
            status_code=404,
            detail=f'Charging point with id {cp_id} not found in system'
        )

    await cp.send_boot_notification()
    return cp.cp_data.dict()


async def execute_heartbeat(
    cp_id: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Executes heartbeat command for provided ChargingPoint id by putting
    heartbeat function in background_tasks.

    :param cp_id: Id of CP for which command will be executed.
    :param background_tasks: FastAPI tool for starting background tasks.
    """
    cp = cp_db.get_cp(cp_id)
    if cp is None:
        logger.warning(
            "Could not find charging point data with id: {}."
            "Boot notification command will be stopped.".format(cp_id)
        )
        raise HTTPException(
            status_code=404,
            detail=f'Charging point with id {cp_id} not found in system'
        )

    background_tasks.add_task(heartbeat, cp)
    return cp.cp_data.dict()
