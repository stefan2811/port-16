import logging
from typing import Optional, Dict

from fastapi.exceptions import HTTPException
from ocpp.v16.enums import AuthorizationStatus

from .storage import StorageService

logger = logging.getLogger(__name__)


class AuthTagService(StorageService):
    """
    This class will be used for storing and retrieving auth tags data
    in/from redis storage.
    """
    MAIN_PATH = 'AUTH_TAG'

    async def add_tag_info(
        self, tag_info: Dict, key: Optional[str] = None,
        command: Optional[str] = None
    ) -> Dict:
        """
        Sets tag_info using provided key. If key is not provided, will be
        created from storage_path and identity. Before setting checks if
        status of tag info is Accepted, if it is not raise an exception.
        Provided command will be used for better logging of warning error.

        :param tag_info: Tag info returned from server side.
        :param command: Command str which will be used for better
            logging of error.
        :param key: Key which will be used for getting/storing tag info data.
        :return: Dict with tag info data
        """
        auth_status = tag_info['status']

        if auth_status == AuthorizationStatus.accepted:
            await self.store_storage_entity(tag_info, key)
            return tag_info
        else:
            log_msg = (
                "Authorization failed with id_tag: {}."
                "Reason: {}".format(self.identity, str(auth_status))
            )
            if command is not None:
                log_msg += '{} command will be stopped.'.format(command)

            logger.warning(log_msg)
            raise HTTPException(
                status_code=403,
                detail=(
                    f'Authorization failed for id_tag {self.identity}, '
                    f'reason: {str(auth_status)}'
                )
            )

    async def validate_tag_id(
        self, key: Optional[str] = None, command: Optional[str] = None
    ) -> Dict:
        """
        Validates info found using provided key. If key is not provided, will
        be created from storage_path and identity. If info not found or
        status of id tag is not Accepted, proper exception will be found.
        Provided command will be used for better logging of warning error.

        :param key: Key which will be used for getting tag info data.
        :param command: Command str which will be used for better
            logging of error.
        :return: Found tag info.
        :rtype: dict
        """
        tag_info = await self.get_storage_entity(key)
        if tag_info.get('status', '') != AuthorizationStatus.accepted:
            log_msg = (
                "Authorization failed with id_tag: {}."
                "Reason: {}".format(self.identity, tag_info['status'])
            )
            if command is not None:
                log_msg += '{} command will be stopped.'.format(command)

            logger.warning(log_msg)
            raise HTTPException(
                status_code=403,
                detail=f'Id tag {self.identity} not valid in system'
            )

        return tag_info
