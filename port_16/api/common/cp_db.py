import logging
from typing import Any, Optional

from fastapi.exceptions import HTTPException

_all_cps = {}
logger = logging.getLogger(__name__)


def get_cp(cp_id: str):
    """
    Gets stored Charging point with provided id or returns None.

    :param cp_id: Id of ChargingPoint which will be returned.
    :return: ChargingPoint with provided id.
    :rtype: port_16.api.common.ocpp.ChargePoint | None
    """
    return _all_cps.get(cp_id)


def set_cp(cp: Any) -> Any:
    """
    Stores provided ChargingPoint in system.

    :param cp: ChargingPoint which will be stored.
    :type cp: port_16.api.common.ChargePoint
    :return: Stored ChargingPoint.
    :rtype: port_16.api.common.ChargePoint
    """
    _all_cps[cp.id] = cp
    return cp


def remove_cp(cp_id: str) -> str:
    """
    Removes stored Charging point with provided id and returns its id.

    :param cp_id: Id of ChargingPoint which will be removed.
    :return: ChargingPoint id.
    :rtype: str
    """
    if cp_id in _all_cps.keys():
        del _all_cps[cp_id]

    # add closing ws connection
    return cp_id


def validate_cp_already_created(cp_id: str) -> None:
    """
    Checks if cp has been already created in system and throws an exception.

    :param cp_id: Identity of CP which will be checked.
    :return:
    """
    cp = get_cp(cp_id)
    if cp is not None:
        logger.warning(
            'Charging point with provided id: '
            '{} already created in system'.format(cp_id)
        )
        raise HTTPException(
            status_code=409,
            detail=f'Charging point with id {cp_id} already created in system'
        )


def validate_and_get(
    cp_id: str, command: Optional[str] = None
):
    """
    Checks if cp is already created in system and throws an exception if not.
    Otherwise, returns found ChargePoint. If command is provided it will be
    used for making better log record.

    :param cp_id: Identity of CP which will be checked.
    :param command: Command which could be blocked if CP is not found.
    :return: Found ChargePoint
    :rtype: port_16.api.common.ocpp.ChargePoint
    """
    cp = get_cp(cp_id)
    if cp is None:
        log_msg = (
            'Charging point not found with provided id: {}'.format(cp_id)
        )
        if command is not None:
            log_msg += '{} command will be stopped.'.format(command)

        logger.warning(log_msg)
        raise HTTPException(
            status_code=404,
            detail=f'Charging point with id {cp_id} not found in system'
        )

    return cp
