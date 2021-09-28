import logging
from functools import partial

import inject
import aioredis

from port_16.ioc import production
from port_16.app_status import ApplicationStatusService, AppStatus

logger = logging.getLogger(__name__)


async def startup_handler():
    redis = await aioredis.create_redis_pool(
        'redis://localhost'
    )
    inject.configure(partial(production(
        instance_kwargs={
            'redis': redis,
        },
        provider_kwargs={
            'status_service': ApplicationStatusService.instance
        }
    )))


async def shutdown_handler():
    redis = inject.instance('redis')
    redis.close()
    await redis.wait_closed()
    logger.info('Redis Connection closed... Shutting down')
    #: :type: :class:`port_16.app_status.ApplicationStatusService`
    status_service = inject.instance('status_service')
    status_service.set_status(AppStatus.EXITING)
    logger.info('Setting app status: {}'.format(
        status_service.get_status())
    )
