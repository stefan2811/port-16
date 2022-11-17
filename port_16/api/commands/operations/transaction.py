import logging
from typing import Dict, Any

from ocpp.v16.enums import ChargePointStatus

from port_16.api.commands.schemas import StartTransaction, StopTransaction
from port_16.api.common import (
    cp_db, ConnectorService, AuthTagService, TransactionService
)

logger = logging.getLogger(__name__)


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
