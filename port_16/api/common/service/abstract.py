import inject

import json
import logging

logger = logging.getLogger(__name__)


class AbstractService:
    """
    This class will be used for storing and retrieving data in/from redis
    storage.
    """
    MAIN_PATH = 'ABSTRACT'

    def __init__(self, cp_id):
        self.cp_id = cp_id
        self.redis_client = inject.instance('redis')

    @property
    def the_key(self):
        """
        Returns created key.

        :return: created key.
        :rtype: str
        """
        return '{}-{}'.format(self.MAIN_PATH, self.cp_id)

    async def get_value(self):
        """
        Gets dict from redis using key.

        :return: Returns value from redis.
        :rtype: dict
        """
        logger.info(
            'Getting value from redis using key: {}'.format(self.the_key)
        )
        data = await self.redis_client.get(self.the_key)
        if data is not None:
            data = json.loads(data)
            logger.info('... and value is found...')

        return data

    async def store_value(self, data):
        """
        Sets dict in redis using key.

        :param data: Dict which will be stored in redis.
        :type data: dict
        :return: Sets and returns data in redis.
        :rtype: dict
        """
        logger.info(
            'Storing value in redis using key: {}'.format(self.the_key)
        )
        await self.redis_client.set(
            self.the_key, json.dumps(data)
        )
        return data

    async def delete_value(self):
        """
        Removes dict from redis using key.

        :return: Removes and returns data in redis.
        :rtype: dict
        """
        logger.info(
            'Deleting value in redis using key: {}'.format(self.the_key)
        )
        data = await self.get_value()
        if data is not None:
            await self.redis_client.delete(
                '{}-{}'.format(self.MAIN_PATH, self.cp_id)
            )
            logger.info('... it is deleted.')

        return data
