import logging
from typing import Optional

from fastapi.exceptions import HTTPException

from .storage import StorageService
from port_16.api.charge_point.schemas import ChargingPointModel

logger = logging.getLogger(__name__)


class ChargePointService(StorageService):
    """
    This class will be used for storing and retrieving charge point data
    in/from redis storage.
    """
    MAIN_PATH = 'CHARGE_POINT'

    async def store_entity(
        self, data: ChargingPointModel, key: Optional[str] = None
    ):
        """
        Sets ChargingPointModel in redis using key. If key is not provided,
        will be created from storage_path and identity.

        :param data: ChargingPointModel model which will be stored in redis.
        :type data: ChargingPointModel
        :param key: Key which will be used for storing value.
        :return: Sets and returns data in redis.
        :rtype: ChargingPointModel
        """
        await self.store_storage_entity(data.dict(), key)
        return data

    async def get_entity(self, key: Optional[str] = None):
        """
        Gets ChargingPointModel from redis using key. If key is not provided,
        will be created from storage_path and identity.

        :param key: Key which will be used for getting value.
        :return: Returns value from redis.
        :rtype: Optional[ChargingPointModel]
        """
        cp_data = await self.get_storage_entity(key)
        if cp_data is not None:
            return ChargingPointModel(**cp_data)

        return None

    async def update_entity(
        self, data: dict, key: Optional[str] = None
    ):
        """
        Merge dict found in redis using key with provided data. If key
        is not provided, will be created from storage_path and identity. If
        data is not found, NotFound exception will be raised.

        :param data: Model data as dict which will be merged and
            stored in redis.
        :type data: dict
        :param key: Key which will be used for storing value.
        :return: Sets and returns data from redis as model instance .
        :rtype: ChargingPointModel
        """
        await self.validate_get_entity(key)
        merged_data = (
            await super(ChargePointService, self).update_storage_entity(
                data, key
            )
        )
        return ChargingPointModel(**merged_data)

    async def validate_get_entity(self, key: Optional[str] = None):
        """
        Gets ChargingPointModel from redis using key. If key is not provided,
        will be created from storage_path and identity. If charge point is not
        found with provided key, NotFound exception will be raised

        :param key: Key which will be used for getting value.
        :return: Returns value from redis.
        :rtype: ChargingPointModel
        """
        model = await self.get_entity(key)
        if model is None:
            the_key = key or self.entity_key
            logger.warning(
                'Charging point not found in redis db '
                'with provided key: {}'.format(the_key)
            )
            raise HTTPException(
                status_code=404,
                detail=(
                    f'Charging point with id {the_key} not found in system'
                )
            )

        return model
