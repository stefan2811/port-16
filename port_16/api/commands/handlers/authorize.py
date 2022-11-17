from typing import Dict, Any

from fastapi import APIRouter

from ..schemas import (
    AuthorizeResponse, AuthorizeRequest,
)
from ..operations import execute_authorize

router = APIRouter()


@router.post(
    path='/{cp_id}/authorize',
    response_model=AuthorizeResponse,
    summary='Executes authorize command',
    description='Uses provided charging point id and executes command',
    response_description='Authorize response',
)
async def authorize_command(
    cp_id: str,
    auth_request: AuthorizeRequest
) -> Dict[str, Any]:
    """
    Executes authorize command for charging point id.

    :param cp_id: Id of ChargingPoint for which command will be executed.
    :param auth_request: Id of tag in request which will be authorized.
    :return: Authorize response
    """
    return await execute_authorize(cp_id, auth_request.id_tag)
