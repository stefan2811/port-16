import logging
from typing import Dict, Any

from fastapi import BackgroundTasks
from ocpp.v16.enums import ChargePointStatus

from port_16.api.charge_point import ChargingPointState
from port_16.api.commands.schemas import StartTransaction, StopTransaction
from port_16.api.common import (
    cp_db, heartbeat, ConnectorService, AuthTagService, TransactionService
)

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


async def execute_authorize(
    cp_id: str,
    id_tag: str
) -> Dict[str, Any]:
    """
    Executes authorize command for provided ChargingPoint using provided
    id_tag.

    :param cp_id: Id of CP for which command will be executed.
    :param id_tag: Id of tag which will be authorized
    """
    cp = cp_db.validate_and_get(cp_id, command='Authorize')
    id_tag_info = await cp.send_authorize(id_tag)
    service = AuthTagService(identity=id_tag)
    logger.info("Type of expire data: {}".format(
        type(id_tag_info['expiry_date'])
    ))
    await service.add_tag_info(id_tag_info, command='Authorize')
    return {'id_tag_info': id_tag_info}


async def execute_start_transaction(
    cp_id: str,
    transaction: StartTransaction
) -> Dict[str, Any]:
    """
    Executes start transaction command for provided ChargingPoint
    using provided data.

    :param cp_id: Id of CP for which command will be executed.
    :param transaction: Transaction data which will be used for starting
        transaction on server side.
    """
    cp = cp_db.validate_and_get(cp_id, command='Start transaction')
    # checks tag id in transaction request
    auth_tag_service = AuthTagService(transaction.id_tag)
    await auth_tag_service.validate_tag_id(command='Start transaction')

    # validate if connector is free for charging
    conn_service = ConnectorService(cp_id)
    await conn_service.validate_connector_used(transaction.connector_id)

    # send start transaction command to server
    transaction_response = await cp.send_start_transaction(transaction)

    # update tag info storage with response
    id_tag_info = await auth_tag_service.add_tag_info(
        transaction_response.id_tag_info, command='Start transaction'
    )

    # sets new state for connector on charger
    await conn_service.update_connector_status(transaction.connector_id)
    await cp.send_connector_status(
        transaction.connector_id, ChargePointStatus.charging
    )

    # updates transaction/connector relation
    trans_service = TransactionService(cp_id)
    transaction_id = transaction_response.transaction_id
    connector_id = transaction.connector_id
    await trans_service.add_transaction(transaction_id, connector_id)

    logger.info('Started transaction {} within cp {} on connector: {}'.format(
        transaction_id, cp_id, transaction.connector_id
    ))
    return {'id_tag_info': id_tag_info}


async def execute_stop_transaction(
    cp_id: str,
    transaction: StopTransaction
) -> Dict[str, Any]:
    """
    Executes stop transaction command for provided ChargingPoint
    using provided data.

    :param cp_id: Id of CP for which command will be executed.
    :param transaction: Transaction data which will be used for stopping
        transaction on server side.
    """
    cp = cp_db.validate_and_get(cp_id, command='Stop transaction')
    # checks tag id in transaction request
    auth_tag_service = AuthTagService(transaction.id_tag)
    await auth_tag_service.validate_tag_id(command='Stop transaction')

    #  check if provided transaction exists in system
    transaction_id = transaction.transaction_id
    trans_service = TransactionService(cp_id)
    await trans_service.validate_transaction_exists(transaction_id)

    id_tag_info = await cp.send_stop_transaction(transaction)

    # update tag info storage with response
    id_tag_info = await auth_tag_service.add_tag_info(
        id_tag_info, command='Stop transaction'
    )

    # update connector and transaction/connector relation
    conn_service = ConnectorService(cp_id)
    connector_id = await trans_service.remove_transaction(transaction_id)

    # sets new state for connector on charger
    await conn_service.update_connector_status(
        connector_id, ChargePointStatus.available
    )
    await cp.send_connector_status(
        connector_id, ChargePointStatus.available
    )

    logger.info('Stopped transaction {} within cp {} on connector: {}'.format(
        transaction_id, cp_id, connector_id
    ))
    return {'id_tag_info': id_tag_info}
