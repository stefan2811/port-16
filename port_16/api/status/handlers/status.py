from typing import Dict

from fastapi import APIRouter

from ..schema.status import StatusResponse


router = APIRouter()


@router.get(
    path='',
    response_model=StatusResponse,
    summary='Server status',
    description='Returns server status information',
    response_description='Status information',
)
async def status() -> Dict[str, str]:
    """Check server status. Will return "OK" and current runtime in seconds
    :return: Status information
    """
    return {
        'application': 'port-16',
        'version': '1.0',
        'status': 'ok',
    }
