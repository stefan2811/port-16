import asyncio
import logging

import websockets
from ocpp.routing import on
from ocpp.v16 import call, call_result
from ocpp.v16 import ChargePoint as OcppCp
from ocpp.v16.enums import FirmwareStatus, Action

from port_16.api.charge_point import cp_db
from port_16.api.charge_point.schemas import (
    ChargingPointModel, ChargingPointState
)

logger = logging.getLogger(__name__)


class ChargePoint(OcppCp):

    def __init__(self, cp_data: ChargingPointModel, *args, **kwargs) -> None:
        kwargs['id'] = cp_data.identity
        super(ChargePoint, self).__init__(*args, **kwargs)
        self.cp_data = cp_data

    async def send_boot_notification(self) -> None:
        request = call.BootNotificationPayload(
            charge_point_model=self.cp_data.model,
            charge_point_vendor=self.cp_data.vendor,
            charge_box_serial_number=self.cp_data.serial_number
        )
        response = await self.call(request)

        if response.status == 'Accepted':
            self.cp_data.state = ChargingPointState.ACCEPTED
            logger.info(
                "CP {} connected to central system.".format(
                    self.cp_data.identity
                )
            )
        else:
            self.cp_data.state = ChargingPointState.REJECTED

    async def heartbeat(self) -> None:
        while True:
            if self.cp_data.state == ChargingPointState.ACCEPTED:
                request = call.HeartbeatPayload()
                response = await self.call(request)
                logger.info(
                    "Heartbeat: {} - {}".format(
                        self.cp_data.identity,
                        str(response.current_time)
                    )
                )
            elif self.cp_data.state == ChargingPointState.UPDATE_FIRMWARE:
                request = call.FirmwareStatusNotificationPayload(
                    status = FirmwareStatus.downloading
                )
                await self.call(request)
                logger.info("CP: {}; Firmware Status Notification: {}.".format(self.cp_data.identity,
                                                                               FirmwareStatus.downloading))
                await asyncio.sleep(1)
                request = call.FirmwareStatusNotificationPayload(
                    status = FirmwareStatus.downloaded
                )
                await self.call(request)
                logger.info("CP: {}; Firmware Status Notification: {}.".format(self.cp_data.identity,
                                                                               FirmwareStatus.downloaded))
                await asyncio.sleep(1)
                request = call.FirmwareStatusNotificationPayload(
                    status = FirmwareStatus.installing
                )
                await self.call(request)
                logger.info("CP: {}; Firmware Status Notification: {}.".format(self.cp_data.identity,
                                                                               FirmwareStatus.installing))
                await asyncio.sleep(1)
                request = call.FirmwareStatusNotificationPayload(
                    status = FirmwareStatus.installed
                )
                await self.call(request)
                logger.info("CP: {}; Firmware Status Notification: {}.".format(self.cp_data.identity,
                                                                               FirmwareStatus.installed))
                self.cp_data.state = ChargingPointState.ACCEPTED

            else:
                logger.info(
                    "Charging point {} is in {} state, "
                    "heartbeat wont be sent".format(
                        self.cp_data.identity,
                        self.cp_data.state
                    )
                )

            await asyncio.sleep(self.cp_data.heartbeat_timeout)


    @on(Action.UpdateFirmware)
    async def on_update_firmware(self, location: str, retrieve_date: str, **kwargs):
        self.cp_data.state = ChargingPointState.UPDATE_FIRMWARE
        return call_result.UpdateFirmwarePayload()


async def heartbeat(cp: ChargePoint):
    logger.info(
        "Starting {} CP heartbeat background task".format(cp.cp_data.identity)
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
