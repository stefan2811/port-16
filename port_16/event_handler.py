import logging
from functools import partial

import inject
import aioredis

from port_16.ioc import production

logger = logging.getLogger(__name__)


async def startup_handler():
    redis = await aioredis.create_redis_pool(
        'redis://localhost'
    )

    inject.configure(partial(production({'redis': redis})))


async def shutdown_handler():
    redis = inject.instance('redis')
    redis.close()
    await redis.wait_closed()
    logger.info('Redis Connection closed... Shutting down')
