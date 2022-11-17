from typing import Dict, Any

from fastapi import APIRouter

from ..schemas import (
    AuthorizeResponse,
    StartTransaction, StopTransaction
)
from ..operations import (
    execute_start_transaction, execute_stop_transaction
)

router = APIRouter()


@router.post(
    path='/{cp_id}/start-transaction',
    response_model=AuthorizeResponse,
    summary='Executes start transaction command',
    description='Uses provided charging point id and executes command',
    response_description='Authorize response',
)
async def start_transaction_command(
    cp_id: str,
    transaction: StartTransaction
) -> Dict[str, Any]:
    """
    Executes start transaction command for charging point id.

    :param cp_id: Id of ChargingPoint for which command will be executed.
    :param transaction: Start transaction request data.
    :return: Authorize response
    """
    return await execute_start_transaction(cp_id, transaction)


@router.post(
    path='/{cp_id}/stop-transaction',
    response_model=AuthorizeResponse,
    summary='Executes stop transaction command',
    description='Uses provided charging point id and executes command',
    response_description='Authorize response',
)
async def stop_transaction_command(
    cp_id: str,
    transaction: StopTransaction
) -> Dict[str, Any]:
    """
    Executes stop transaction command for charging point id.

    :param cp_id: Id of ChargingPoint for which command will be executed.
    :param transaction: Stop transaction request data.
    :return: Authorize response
    """
    return await execute_stop_transaction(cp_id, transaction)
