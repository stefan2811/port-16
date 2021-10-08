import logging
from typing import Optional, Dict

from ocpp.v16.enums import ChargePointStatus
from fastapi.exceptions import HTTPException

from .storage import StorageService

logger = logging.getLogger(__name__)


class ConnectorService(StorageService):
    """
    This class will be used for storing and retrieving connector data
    in/from redis storage.
    """
    MAIN_PATH = 'CONNECTOR'

    async def start_charging_point(
        self, connector_number: int, key: Optional[str] = None
    ) -> Dict[int, ChargePointStatus]:
        """
        Sets charging point status for provided connector number and provided
        key. If key is not provided, will be created from storage_path and
        identity. If connectors data are found in redis it will be used,
        otherwise Available state will be used.

        :param connector_number: Number of connectors within charging point.
        :param key: Key which will be used for getting connectors data.
        :return: Dict with connector ids and theirs status.
        """
        redis_data = await self.get_storage_entity(key)
        connectors_data = {}
        for i in range(0, connector_number):
            if redis_data is not None:
                conn_value = redis_data[str(i+1)]
            else:
                conn_value = ChargePointStatus.available.value

            connectors_data.update({str((i+1)): conn_value})

        await self.update_storage_entity(connectors_data, key)
        return {
            int(key): ChargePointStatus(value)
            for key, value in connectors_data.items()
        }

    async def validate_connector_used(
        self, connector_id: int, key: Optional[str] = None
    ) -> Dict[int, ChargePointStatus]:
        """
        Checks if provided connector id is free and using provided key.
        If key is not provided, will be created from storage_path and
        identity. If connectors data are not found in redis NotFound
        exception will be raised. If connector with provided id is not
        in available state, Conflict exception will be raised.

        :param connector_id: Id of connector within charging point which will
            be checked.
        :param key: Key which will be used for getting connectors data.
        :return: Dict with connector ids and theirs status.
        """
        redis_data = await self.get_storage_entity(key)
        if redis_data is None:
            logger.warning(
                'Charging point not found in redis db '
                'with provided key: {}'.format(self.identity)
            )
            raise HTTPException(
                status_code=404,
                detail=(
                    f'Charging point with id {self.identity} '
                    f'not found in system'
                )
            )

        if str(connector_id) not in redis_data.keys():
            logger.warning(
                'Connector id: {} not found within '
                'Charging point: {}'.format(connector_id, self.identity)
            )
            raise HTTPException(
                status_code=404,
                detail=(
                    f'Connector id {connector_id} not found within Charging '
                    f'point with id {self.identity}'
                )
            )

        connector_status = ChargePointStatus(redis_data[str(connector_id)])
        if connector_status != ChargePointStatus.available:
            the_key = key or self.entity_key
            logger.warning(
                'Connector id: {} is not available within '
                'Charging point: {}'.format(connector_id, the_key)
            )
            raise HTTPException(
                status_code=409,
                detail=(
                    f'Connector id {connector_id} is not available '
                    f'within Charging point with id {the_key}'
                )
            )

        return {
            int(key): ChargePointStatus(value)
            for key, value in redis_data.items()
        }

    async def update_connector_status(
        self,
        connector_id: int,
        status: ChargePointStatus = ChargePointStatus.charging,
        key: Optional[str] = None
    ) -> Dict[int, ChargePointStatus]:
        """
        Updates connector status with provided connector id and using
        provided key. If key is not provided, will be created from
        storage_path and identity.

        :param connector_id: Id of connector within charging point which will
            be updated.
        :param status: Status which will be value for connector id.
        :param key: Key which will be used for getting connectors data.
        :return: Dict with connector ids and theirs status.
        """
        merged_data = await self.update_storage_entity(
            {str(connector_id): status.value},
            key
        )
        return {
            int(key): ChargePointStatus(value)
            for key, value in merged_data.items()
        }
