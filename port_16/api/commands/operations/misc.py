import logging
from typing import Dict, Any

from fastapi import BackgroundTasks

from port_16.api.charge_point import ChargingPointState
from port_16.api.common import cp_db, heartbeat, ConnectorService

logger = logging.getLogger(__name__)


async def execute_boot_notification(cp_id: str) -> Dict[str, Any]:
    """
    Executes boot notification command for provided ChargingPoint id.

    :param cp_id: Id of CP for which command will be executed.
    """
    cp = cp_db.validate_and_get(cp_id, command='Boot notification')
    cp_model = await cp.cp_service.validate_get_entity()
    cp_model = await cp.send_boot_notification(cp_model.heartbeat)
    conn_service = ConnectorService(cp_id)
    if ChargingPointState(cp_model.state) == ChargingPointState.ACCEPTED:
        connector_data = await conn_service.start_charging_point(
            cp_model.connector_number
        )
        for key, value in connector_data.items():
            await cp.send_connector_status(key, value)

    return cp_model.dict()


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
    cp = cp_db.validate_and_get(cp_id, command='Heartbeat')
    cp_model = await cp.cp_service.validate_get_entity()
    background_tasks.add_task(heartbeat, cp)
    return cp_model.dict()
