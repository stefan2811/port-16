import logging
from typing import Optional, Dict

from fastapi.exceptions import HTTPException

from .storage import StorageService

logger = logging.getLogger(__name__)


class TransactionService(StorageService):
    """
    This class will be used for storing and retrieving transaction data
    in/from redis storage.
    """
    MAIN_PATH = 'TRANSACTION'

    async def add_transaction(
        self,
        transaction_id: int,
        connector_id: int,
        key: Optional[str] = None
    ) -> Dict[int, str]:
        """
        Adds transaction id and connector id relation for provided key. If
        key is not provided, will be created from storage_path and identity.

        :param transaction_id: Id of transaction.
        :param connector_id: Id of connector.
        :param key: Key which will be used for getting trans/connector data.
        :return: Dict with transaction id and connector id relations.
        """
        updated_data = await self.update_storage_entity(
            {str(transaction_id): connector_id},
            key
        )
        return {
            int(key): int(value)
            for key, value in updated_data.items()
        }

    async def validate_transaction_exists(
        self, transaction_id: int, key: Optional[str] = None
    ) -> Dict[int, str]:
        """
        Checks if provided connector id exists in system using provided key.
        If key is not provided, will be created from storage_path and
        identity. If transaction data are not found in redis NotFound
        exception will be raised.

        :param transaction_id: Id of transaction within which will
            be checked.
        :param key: Key which will be used for getting transaction data.
        :return: Dict with transaction ids and theirs connectors.
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

        if str(transaction_id) not in redis_data.keys():
            logger.warning(
                'Transaction id: {} not found within '
                'Charging point: {}'.format(transaction_id, self.identity)
            )
            raise HTTPException(
                status_code=404,
                detail=(
                    f'Transaction id {transaction_id} not found '
                    f'within Charging point with id {self.identity}'
                )
            )

        return {
            int(key): int(value) for key, value in redis_data.items()
        }

    async def remove_transaction(
        self,
        transaction_id: int,
        key: Optional[str] = None
    ) -> int:
        """
        Removes transaction/connector relation for provided transaction_id
        using provided key. If key is not provided, will be created from
        storage_path and identity. Returns connector_id found on relation.

        :param transaction_id: Id of transaction within which will be removed.
        :param key: Key which will be used for getting transaction data.
        :return: Id of connector.
        """
        redis_data = await self.get_storage_entity(key)
        connector_id = redis_data.get(str(transaction_id))
        del redis_data[str(transaction_id)]
        await self.store_storage_entity(redis_data, key)
        return connector_id
