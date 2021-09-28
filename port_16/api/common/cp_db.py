from typing import Any, Optional

_all_cps = {}


def get_cp(cp_id: str) -> Optional[Any]:
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
    _all_cps[cp.cp_data.identity] = cp
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
