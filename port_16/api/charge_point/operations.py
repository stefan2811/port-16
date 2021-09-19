import logging
from typing import Dict, Any

from fastapi import BackgroundTasks
from fastapi.exceptions import HTTPException
from ocpp.v16.enums import AuthorizationStatus

from port_16.api.charge_point import cp_db
from port_16.api.charge_point.schemas import (
    ChargingPointModel, StartTransaction, StopTransaction
)
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
            "Heartbeat command will be stopped.".format(cp_id)
        )
        raise HTTPException(
            status_code=404,
            detail=f'Charging point with id {cp_id} not found in system'
        )

    background_tasks.add_task(heartbeat, cp)
    return cp.cp_data.dict()


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
    #: :type: :class:`port_16.api.charge_point.service.ChargePoint`
    cp = cp_db.get_cp(cp_id)
    if cp is None:
        logger.warning(
            "Could not find charging point data with id: {}."
            "Authorize command will be stopped.".format(cp_id)
        )
        raise HTTPException(
            status_code=404,
            detail=f'Charging point with id {cp_id} not found in system'
        )

    id_tag_info = await cp.send_authorize(id_tag)
    logger.info("Type of expire data: {}".format(
        type(id_tag_info['expiry_date'])
    ))
    auth_status = id_tag_info['status']
    # implement auth list and caching later
    if auth_status == AuthorizationStatus.accepted:
        cp.set_id_tag_info(id_tag, id_tag_info)
        return {'id_tag_info': id_tag_info}
    else:
        logger.warning(
            "Authorization failed with id_tag: {} on cp {}."
            "Reason {}.".format(
                id_tag, cp_id, str(auth_status)
            )
        )
        raise HTTPException(
            status_code=403,
            detail=(
                f'Authorization failed for id_tag {id_tag}, '
                f'reason: {str(auth_status)}'
            )
        )


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
    #: :type: :class:`port_16.api.charge_point.service.ChargePoint`
    cp = cp_db.get_cp(cp_id)
    if cp is None:
        logger.warning(
            "Could not find charging point data with id: {}."
            "Start transaction command will be stopped.".format(cp_id)
        )
        raise HTTPException(
            status_code=404,
            detail=f'Charging point with id {cp_id} not found in system'
        )

    # checks tag id in transaction request
    id_tag = transaction.id_tag
    tag_info = cp.cp_data.tags.get(id_tag, {})
    if tag_info.get('status', '') != AuthorizationStatus.accepted:
        logger.warning(
            "Id tag {} is not authenticated properly."
            "Start transaction command will be stopped.".format(id_tag)
        )
        raise HTTPException(
            status_code=403,
            detail=f'Id tag {id_tag} not valid in system'
        )

    transaction_response = await cp.send_start_transaction(transaction)
    id_tag_info = transaction_response.id_tag_info
    auth_status = id_tag_info['status']
    # implement auth list and caching later
    if auth_status == AuthorizationStatus.accepted:
        cp.set_id_tag_info(id_tag, id_tag_info)
        logger.info('Started transaction {} on cp {}'.format(
            transaction_response.transaction_id, cp_id
        ))
        await cp.set_transaction_connector(
            transaction_response.transaction_id, transaction.connector_id
        )
        return {'id_tag_info': id_tag_info}
    else:
        logger.warning(
            "Start transaction failed with id tag: {} on cp {}."
            "Reason {}.".format(
                id_tag, cp_id, str(auth_status)
            )
        )
        raise HTTPException(
            status_code=403,
            detail=(
                f'Start transaction for id_tag {id_tag}, '
                f'reason: {str(auth_status)}'
            )
        )


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
    #: :type: :class:`port_16.api.charge_point.service.ChargePoint`
    cp = cp_db.get_cp(cp_id)
    if cp is None:
        logger.warning(
            "Could not find charging point data with id: {}."
            "Start transaction command will be stopped.".format(cp_id)
        )
        raise HTTPException(
            status_code=404,
            detail=f'Charging point with id {cp_id} not found in system'
        )

    # checks tag id in transaction request
    id_tag = transaction.id_tag
    if id_tag is not None:
        tag_info = cp.cp_data.tags.get(id_tag, {})
        if tag_info.get('status', '') != AuthorizationStatus.accepted:
            logger.warning(
                "Id tag {} is not authenticated properly."
                "Start transaction command will be stopped.".format(id_tag)
            )
            raise HTTPException(
                status_code=403,
                detail=f'Id tag {id_tag} not valid in system'
            )

    #  check if provided transaction exists in system
    if cp.cp_data.transactions.get(transaction.transaction_id) is None:
        logger.warning(
            "Stop transaction failed with id tag: {} on cp {}."
            "Reason transaction {} not found.".format(
                id_tag, cp_id, str(transaction.transaction_id)
            )
        )
        raise HTTPException(
            status_code=403,
            detail=(
                f'Stop transaction for id_tag {id_tag}, reason transaction: '
                f'{str(transaction.transaction_id)} not found'
            )
        )

    transaction_response = await cp.send_stop_transaction(transaction)
    id_tag_info = transaction_response
    auth_status = id_tag_info['status']
    # implement auth list and caching later
    if auth_status == AuthorizationStatus.accepted:
        cp.set_id_tag_info(id_tag, id_tag_info)
        await cp.release_transaction_connector(
            transaction.transaction_id
        )
        return {'id_tag_info': id_tag_info}
    else:
        logger.warning(
            "Stop transaction failed with id tag: {} on cp {}."
            "Reason {}.".format(
                id_tag, cp_id, str(auth_status)
            )
        )
        raise HTTPException(
            status_code=403,
            detail=(
                f'Stop transaction for id_tag {id_tag}, '
                f'reason: {str(auth_status)}'
            )
        )
