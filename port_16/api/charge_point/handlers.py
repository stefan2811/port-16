from typing import Dict, Any

from fastapi import APIRouter, BackgroundTasks

from .schemas import ChargingPointModel
from .operations import (
    create_charging_point, get_charging_point, delete_charging_point,
)

router = APIRouter()


@router.get(
    path='/{cp_id}',
    response_model=ChargingPointModel,
    summary='Find charging point in system',
    description='Returns charging point with provided id',
    response_description='Found charging point data',
)
async def get_cp(cp_id: str) -> Dict[str, Any]:
    """
    Gets charging point in system and returns data.

    :return: Charging point data.
    """
    return get_charging_point(cp_id)


@router.post(
    path='',
    response_model=ChargingPointModel,
    summary='Charging point creation',
    description='Creates and returns charging point',
    response_description='Created charging point data',
)
async def create_cp(
    create_model: ChargingPointModel,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Creates charging point in system and returns created data.

    :return: Crated charging point data.
    """
    return create_charging_point(create_model, background_tasks)


@router.delete(
    path='/{cp_id}',
    response_model=ChargingPointModel,
    summary='Deletes charging point in system',
    description='Returns deleted charging point with provided id',
    response_description='Deleted charging point data',
)
async def delete_cp(cp_id: str) -> Dict[str, Any]:
    """
    Deletes charging point in system and returns data.

    :return: Deleted charging point data.
    """
    return delete_charging_point(cp_id)
