import inject

import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class StorageService:
    """
    This class will be used for storing and retrieving data in/from redis
    storage.
    """
    MAIN_PATH = 'STORAGE'

    def __init__(
        self,
        identity: str,
        storage_path: Optional[str] = None
    ):
        self.identity = identity
        self.storage_path = storage_path or self.MAIN_PATH
        self.redis_client = inject.instance('redis')

    @property
    def entity_key(self):
        """
        Returns created key.

        :return: created key.
        :rtype: str
        """
        return '{}-{}'.format(self.storage_path, self.identity)

    @property
    def all_keys_key(self):
        """
        Creates all_keys key which will be used for getting/storing all
        entity keys list.

        :return: All keys key.
        :rtype: str
        """
        return '{}-KEYS'.format(self.storage_path)

    async def get_all_keys(self):
        """
        Returns all keys stored within storage_path.

        :return: Returns all keys stored within storage_path.
        :rtype: list of str
        """
        data = await self.redis_client.get(self.all_keys_key)
        if data is not None:
            data = json.loads(data)
        else:
            data = []

        return data

    async def add_new_key(self, key: Optional[str] = None):
        """
        Adds and stores provided key in all_keys list. If key is not provided,
        identity value will be used.

        :param key: Key which will be used for storing. If is not provided,
            identity value will be used.
        :return: List of updated list.
        :rtype: list of str
        """
        new_key = key or self.identity
        all_keys = await self.get_all_keys()
        if new_key not in all_keys:
            all_keys.append(new_key)
            content = json.dumps(all_keys)
            await self.redis_client.set(self.all_keys_key, content)

        return all_keys

    async def remove_key(self, key: Optional[str] = None):
        """
        Removes provided key in all_keys list and stores it in storage. If
        key is not provided, identity value will be used.

        :param key: Key which will be used for updating list. If is
            not provided, identity value will be used.
        :return: List of updated list.
        :rtype: list of str
        """
        removing_key = key or self.identity
        all_keys = await self.get_all_keys()
        if removing_key in all_keys:
            all_keys.remove(removing_key)
            content = json.dumps(all_keys)
            await self.redis_client.set(self.all_keys_key, content)

        return all_keys

    async def get_all_storage_entities(self):
        """
        Gets all stored entities within storage path.

        :return: All stored entities within storage path.
        :rtype: dict
        """
        result = {}
        for key in await self.get_all_keys():
            result.update({
                key: json.loads(await self.redis_client.get(
                    '{}-{}'.format(self.storage_path, key)
                ))
            })

        return result

    async def get_storage_entity(self, key: Optional[str] = None):
        """
        Gets dict from redis using key. If key is not provided, will be
        created from storage_path and identity.

        :param key: Key which will be used for getting value.
        :return: Returns value from redis.
        :rtype: dict
        """
        the_key = key or self.entity_key
        logger.info(
            'Getting value from redis using key: {}'.format(the_key)
        )
        data = await self.redis_client.get(the_key)
        if data is not None:
            await self.add_new_key()
            data = json.loads(data)
            logger.info('... and value is found...')

        return data

    async def store_storage_entity(self, data, key: Optional[str] = None):
        """
        Sets dict in redis using key. If key is not provided, will be
        created from storage_path and identity.

        :param data: Dict or str which will be stored in redis.
        :type data: dict | str
        :param key: Key which will be used for storing value.
        :return: Sets and returns data in redis.
        :rtype: dict
        """
        the_key = key or self.entity_key
        logger.info(
            'Storing value in redis using key: {}'.format(the_key)
        )
        content = json.dumps(data) if isinstance(data, dict) else data
        await self.redis_client.set(the_key, content)
        return data

    async def delete_storage_entity(self, key: Optional[str] = None):
        """
        Removes dict from redis using key. If key is not provided, will be
        created from storage_path and identity.

        :param key: Key which will be used for deleting value.
        :return: Removes and returns data in redis.
        :rtype: dict
        """
        the_key = key or self.entity_key
        logger.info(
            'Deleting value in redis using key: {}'.format(the_key)
        )
        data = await self.get_storage_entity()
        if data is not None:
            await self.remove_key()
            await self.redis_client.delete(the_key)
            logger.info('... it is deleted.')

        return data

    async def update_storage_entity(self, data, key: Optional[str] = None):
        """
        Merge dict found in redis using key with provided data. If key is
        not provided, will be created from storage_path and identity.

        :param data: Dict which will be merged and stored in redis.
        :type data: dict
        :param key: Key which will be used for storing value.
        :return: Sets and returns data in redis.
        :rtype: dict
        """
        the_key = key or self.entity_key
        logger.info(
            'Merging value in redis using key: {}'.format(the_key)
        )
        redis_data = await self.get_storage_entity()
        if redis_data is not None:
            redis_data.update(data)
        else:
            redis_data = data

        await self.redis_client.set(
            the_key, json.dumps(redis_data)
        )
        return redis_data
