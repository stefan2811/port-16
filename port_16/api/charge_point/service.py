import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

import websockets
from ocpp.v16 import call
from ocpp.v16 import ChargePoint as OcppCp
from ocpp.v16.call_result import StartTransactionPayload
from ocpp.v16.enums import ChargePointStatus, ChargePointErrorCode

from port_16.api.charge_point import cp_db
from port_16.api.charge_point.schemas import (
    ChargingPointModel, ChargingPointState,
    StartTransaction, StopTransaction
)

logger = logging.getLogger(__name__)


class ChargePoint(OcppCp):

    def __init__(self, cp_data: ChargingPointModel, *args, **kwargs) -> None:
        kwargs['id'] = cp_data.identity
        super(ChargePoint, self).__init__(*args, **kwargs)
        self.cp_data = cp_data

    async def send_connector_status(
        self, connector_id: id,
        status: ChargePointStatus = ChargePointStatus.available,
        error_code: ChargePointErrorCode = ChargePointErrorCode.no_error
    ):
        request = call.StatusNotificationPayload(
            connector_id=connector_id,
            error_code=error_code,
            status=status
        )
        await self.call(request)
        self.cp_data.connectors.update({
            connector_id: status
        })
        logger.info(
            'Connector {} of CP {} is in status: {}'.format(
                connector_id, self.cp_data.identity, status.value
            )
        )

    async def send_boot_notification(self) -> None:
        request = call.BootNotificationPayload(
            charge_point_model=self.cp_data.model,
            charge_point_vendor=self.cp_data.vendor,
            charge_box_serial_number=self.cp_data.serial_number
        )
        #: :type: :class:`ocpp.v16.call_result.BootNotificationPayload`
        response = await self.call(request)

        if response.status == 'Accepted':
            self.cp_data.state = ChargingPointState.ACCEPTED
            logger.info(
                "CP {} connected to central system.".format(
                    self.cp_data.identity
                )
            )
            for i in range(0, self.cp_data.connector_number):
                await self.send_connector_status(i + 1)
                self.cp_data.connectors.update({
                    (i+1): ChargePointStatus.available
                })
        else:
            self.cp_data.state = ChargingPointState.REJECTED

    async def heartbeat(self) -> None:
        while True:
            if self.cp_data.state == ChargingPointState.ACCEPTED:
                request = call.HeartbeatPayload()
                #: :type: :class:`ocpp.v16.call_result.HeartbeatPayload`
                response = await self.call(request)
                logger.info(
                    "Heartbeat: {} - {}".format(
                        self.cp_data.identity,
                        str(response.current_time)
                    )
                )
            else:
                logger.info(
                    "Charging point {} is in {} state, "
                    "heartbeat wont be sent".format(
                        self.cp_data.identity,
                        self.cp_data.state
                    )
                )

            await asyncio.sleep(self.cp_data.heartbeat_timeout)

    async def send_authorize(self, id_tag: str) -> Dict[str, Any]:
        request = call.AuthorizePayload(
            id_tag=id_tag
        )
        #: :type: :class:`ocpp.v16.call_result.AuthorizePayload`
        response = await self.call(request)
        return response.id_tag_info

    def set_id_tag_info(self, id_tag: str, tag_info: dict):
        self.cp_data.tags.update({
            id_tag: tag_info
        })

    async def set_transaction_connector(
        self, transaction_id: int, connector_id: int
    ):
        self.cp_data.transactions.update({
            transaction_id: connector_id
        })
        await self.send_connector_status(
            connector_id, ChargePointStatus.charging
        )

    async def release_transaction_connector(
        self, transaction_id: int
    ):
        connector_id = self.cp_data.transactions[transaction_id]
        await self.send_connector_status(
            connector_id, ChargePointStatus.available
        )
        del self.cp_data.transactions[transaction_id]

    async def send_start_transaction(
        self, transaction: StartTransaction
    ) -> StartTransactionPayload:
        request = call.StartTransactionPayload(
            connector_id=transaction.connector_id,
            id_tag=transaction.id_tag,
            meter_start=transaction.meter_start,
            timestamp=datetime.utcnow().isoformat()
        )
        #: :type: :class:`ocpp.v16.call_result.StartTransactionPayload`
        return await self.call(request)

    async def send_stop_transaction(
        self, transaction: StopTransaction
    ) -> Dict[str, Any]:
        request = call.StopTransactionPayload(
            transaction_id=transaction.transaction_id,
            meter_stop=transaction.meter_stop,
            timestamp=datetime.utcnow().isoformat(),
            id_tag=transaction.id_tag,
            reason=transaction.reason,
            # add providing meter values
        )
        #: :type: :class:`ocpp.v16.call_result.StopTransactionPayload`
        response = await self.call(request)
        return response.id_tag_info


async def heartbeat(cp: ChargePoint):
    logger.info(
        "Starting {} CP heartbeat background task".format(
            cp.cp_data.identity
        )
    )
    await cp.heartbeat()


async def start_cp(cp_data: ChargingPointModel):
    logger.info("Starting {} CP and background task".format(cp_data.identity))
    async with websockets.connect(
        uri=cp_data.ws_uri,
        subprotocols=[cp_data.protocol]
    ) as ws:
        cp = ChargePoint(cp_data=cp_data, connection=ws)
        cp_db.set_cp(cp)
        await cp.start()
