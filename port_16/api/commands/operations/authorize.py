import logging
from typing import Dict, Any

from port_16.api.common import cp_db, AuthTagService

logger = logging.getLogger(__name__)


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
