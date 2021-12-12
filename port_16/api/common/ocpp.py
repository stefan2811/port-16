import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

import inject
import websockets
from ocpp.routing import on, after
from ocpp.v16 import call, call_result
from ocpp.v16 import ChargePoint as OcppCp
from ocpp.v16.enums import (
    FirmwareStatus, Action, DiagnosticsStatus,
    ChargePointStatus, ChargePointErrorCode, RegistrationStatus,
    RemoteStartStopStatus, AvailabilityStatus, AvailabilityType,
    ResetType, ResetStatus
)

from port_16.api.common import cp_db
from port_16.app_status import AppStatus
from port_16.api.common.service import *
from port_16.api.commands import StartTransaction, StopTransaction
from port_16.api.charge_point import (
    ChargingPointModel, ChargingPointState, HeartbeatModel
)

logger = logging.getLogger(__name__)


# noinspection PyUnusedLocal
class ChargePoint(OcppCp):

    def __init__(self, *args, **kwargs) -> None:
        super(ChargePoint, self).__init__(*args, **kwargs)
        self.cp_service = ChargePointService(self.id)

    async def send_connector_status(
        self, connector_id: int,
        status: ChargePointStatus = ChargePointStatus.available,
        error_code: ChargePointErrorCode = ChargePointErrorCode.no_error
    ):
        request = call.StatusNotificationPayload(
            connector_id=connector_id,
            error_code=error_code,
            status=status
        )
        await self.call(request)
        logger.info(
            'Connector {} of CP {} is in status: {}'.format(
                connector_id, self.id, status.value
            )
        )

    async def send_boot_notification(
        self, heartbeat_model: HeartbeatModel
    ) -> ChargingPointModel:
        request = call.BootNotificationPayload(
            charge_point_model=heartbeat_model.model,
            charge_point_vendor=heartbeat_model.vendor,
            charge_box_serial_number=heartbeat_model.serial_number
        )
        #: :type: :class:`ocpp.v16.call_result.BootNotificationPayload`
        response = await self.call(request)

        if response.status == RegistrationStatus.accepted:
            cp_model = await self.cp_service.update_entity(data={
                'state': ChargingPointState.ACCEPTED.value
            })
            logger.info(
                "CP {} connected to central system.".format(self.id)
            )
        else:
            cp_model = await self.cp_service.update_entity(data={
                'state': ChargingPointState.REJECTED.value
            })
            logger.info(
                "CP {} rejected by central system.".format(self.id)
            )

        return cp_model

    async def send_firmware_notification(
        self, status: FirmwareStatus, sleep_time: int = 1
    ) -> None:
        logger.info(
            'Sending and setting Firmware Status Notification: {} for CP {}. '
            'It will last for {} seconds'.format(
                status, self.id,  sleep_time
            )
        )
        request = call.FirmwareStatusNotificationPayload(
            status=status
        )
        await self.call(request)
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)

    async def send_diagnostics_notification(
        self, status: DiagnosticsStatus, sleep_time: int = 1
    ) -> None:
        logger.info(
            'Sending and setting Diagnostics Status Notification: {} '
            'for CP {}. It will last for {} seconds'.format(
                status, self.id, sleep_time
            )
        )
        request = call.DiagnosticsStatusNotificationPayload(
            status=status
        )
        await self.call(request)
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)

    async def _simulate_update_firmware(self) -> None:
        # Downloading
        await self.send_firmware_notification(FirmwareStatus.downloading)
        # Downloaded
        await self.send_firmware_notification(FirmwareStatus.downloading)
        # Installing
        await self.send_firmware_notification(FirmwareStatus.installing)
        # Installed
        await self.send_firmware_notification(FirmwareStatus.installed, -1)

        # Charging point available again
        await self.cp_service.update_entity(data={
            'state': ChargingPointState.ACCEPTED.value
        })
        logger.info(
            'After firmware update, CP {} returned '
            'into ACCEPTED state'.format(self.id)
        )

    async def _simulate_upload_diagnostics(self) -> None:
        # Uploading
        await self.send_diagnostics_notification(
            DiagnosticsStatus.uploading
        )
        # Uploaded
        await self.send_diagnostics_notification(
            DiagnosticsStatus.uploaded, -1
        )

        # Charging point available again
        await self.cp_service.update_entity(data={
            'state': ChargingPointState.ACCEPTED.value
        })
        logger.info(
            'After firmware update, CP {} returned '
            'into ACCEPTED state'.format(self.id)
        )

    async def heartbeat(self) -> None:
        while True:
            cp_model = await self.cp_service.validate_get_entity()
            cp_state = ChargingPointState(cp_model.state)
            if cp_state == ChargingPointState.ACCEPTED:
                request = call.HeartbeatPayload()
                #: :type: :class:`ocpp.v16.call_result.HeartbeatPayload`
                response = await self.call(request)
                logger.info(
                    "Heartbeat for CP: {} done at {}".format(
                        self.id, str(response.current_time)
                    )
                )
            elif cp_state == ChargingPointState.UPDATE_FIRMWARE:
                await self._simulate_update_firmware()
            elif cp_state == ChargingPointState.GET_DIAGNOSTICS:
                await self._simulate_upload_diagnostics()
            else:
                logger.info(
                    "Charging point {} is in {} state, heartbeat wont be "
                    "sent".format(self.id, cp_state)
                )

            await asyncio.sleep(cp_model.heartbeat.timeout)
            #: :type: :class:`port_16.app_status.ApplicationStatusService`
            status_service = inject.instance('status_service')
            if status_service.get_status() == AppStatus.EXITING:
                logger.info(
                    'Application is in Shutting down state.. Exiting '
                    'from heartbeat background process..'
                )
                return

    async def send_authorize(self, id_tag: str) -> Dict[str, Any]:
        request = call.AuthorizePayload(
            id_tag=id_tag
        )
        #: :type: :class:`ocpp.v16.call_result.AuthorizePayload`
        response = await self.call(request)
        return response.id_tag_info

    async def send_start_transaction(
        self, transaction: StartTransaction
    ) -> call_result.StartTransactionPayload:
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

    @on(Action.UpdateFirmware)
    async def on_update_firmware(
        self, location: str, retrieve_date: str, **kwargs
    ) -> call_result.UpdateFirmwarePayload:
        await self.cp_service.update_entity(data={
            'state': ChargingPointState.UPDATE_FIRMWARE.value
        })
        logger.info(
            'Starting UpdateFirmware process for CP {}'.format(self.id)
        )
        return call_result.UpdateFirmwarePayload()

    @on(Action.GetDiagnostics)
    async def on_get_diagnostics(
        self, location: str, **kwargs
    ) -> call_result.GetDiagnosticsPayload:
        await self.cp_service.update_entity(data={
            'state': ChargingPointState.GET_DIAGNOSTICS.value
        })
        logger.info(
            'Starting GetDiagnostics process for CP {}'.format(self.id)
        )
        return call_result.GetDiagnosticsPayload(
            file_name=self.id
        )

    @on(Action.RemoteStartTransaction)
    async def on_remote_start_transaction(
            self, connector_id: int, id_tag: str, **kwargs
    ) -> call_result.RemoteStartTransactionPayload:
        return call_result.RemoteStartTransactionPayload(
            status=RemoteStartStopStatus.accepted
        )

    @after(Action.RemoteStartTransaction)
    async def after_remote_start_transaction(
            self, connector_id: int, id_tag: str, **kwargs
    ) -> call_result.RemoteStartTransactionPayload:
        timestamp = datetime.utcnow().isoformat()
        logger.info(
            'Starting transaction on CP: {} using card with Id: {} '
            'on connector: {}, start_time: {}'.format(
                self.id, id_tag, connector_id, timestamp
            )
        )
        remote_start_transaction = StartTransaction.construct(connector_id=connector_id,
                                                            id_tag=id_tag,
                                                            timestamp=timestamp)
        cp = cp_db.validate_and_get(self.id, command='Start transaction')
        conn_service = ConnectorService(self.id)
        trans_service = TransactionService(self.id)

        authorize = await self.send_authorize(id_tag)

        if authorize.get('status') == 'Accepted':
            send_start_transaction = await self.send_start_transaction(remote_start_transaction)
            await conn_service.update_connector_status(connector_id)
            await cp.send_connector_status(
                connector_id, ChargePointStatus.charging
            )
            await trans_service.add_transaction(send_start_transaction.transaction_id, connector_id)

    @on(Action.RemoteStopTransaction)
    async def on_remote_stop_transaction(
            self, transaction_id: int, **kwargs
    ) -> call_result.RemoteStopTransactionPayload:
        return call_result.RemoteStopTransactionPayload(
            status=RemoteStartStopStatus.accepted
        )

    @after(Action.RemoteStopTransaction)
    async def after_remote_stop_transaction(
            self, transaction_id: int, **kwargs
    ) -> call_result.RemoteStopTransactionPayload:
        logger.info(
            'Stop transaction on CP: {} with transaction id: {} '.format(
                self.id, transaction_id
            )
        )
        remoteStopTransaction = StopTransaction.construct(transaction_id=transaction_id)
        cp = cp_db.validate_and_get(self.id, command='Stop transaction')

        trans_service = TransactionService(self.id)
        await trans_service.validate_transaction_exists(transaction_id)

        id_tag_info = await self.send_stop_transaction(remoteStopTransaction)

        conn_service = ConnectorService(self.id)
        connector_id = await trans_service.remove_transaction(transaction_id)

        # sets new state for connector on charger
        await conn_service.update_connector_status(
            connector_id, ChargePointStatus.available
        )
        await cp.send_connector_status(
            connector_id, ChargePointStatus.available
        )

    @on(Action.ChangeAvailability)
    async def on_change_availability(
            self, connector_id: int, type: AvailabilityType
    ) -> call_result.ChangeAvailabilityPayload:
        return call_result.ChangeAvailabilityPayload(
            status=AvailabilityStatus.accepted
        )

    @after(Action.ChangeAvailability)
    async def after_change_availability(
            self, connector_id: int, type: AvailabilityType
    ) -> call_result.ChangeAvailabilityPayload:
        logger.info(
            'Change availability on CP: {} - connector: {} to: {} '.format(
                self.id, connector_id, type
            )
        )
        cp = cp_db.validate_and_get(self.id, command='Change Availability')
        conn_service = ConnectorService(self.id)
        await conn_service.check_connector_exists(connector_id)

        # sets new state for connector on charger
        if type == AvailabilityType.inoperative:
            await conn_service.update_connector_status(
                connector_id, ChargePointStatus.unavailable
            )
            # send status notification
            await cp.send_connector_status(
                connector_id, ChargePointStatus.unavailable
            )

        elif type == AvailabilityType.operative:
            await conn_service.update_connector_status(
                connector_id, ChargePointStatus.available
            )
            # send status notification
            await cp.send_connector_status(
                connector_id, ChargePointStatus.available
            )

    @on(Action.Reset)
    async def on_reset(
            self, type: ResetType
    ) -> call_result.ResetPayload:
        logger.info(
            'Reset CP: {} '.format(self.id)
        )
        return call_result.ResetPayload(
            status=ResetStatus.accepted
        )

    @after(Action.Reset)
    async def after_reset(
            self, type: ResetType
    ) -> call_result.ResetPayload:
        logger.info(
            'Boot after reset CP: {} '.format(self.id)
        )
        heartbeat_model = HeartbeatModel()
        await self.send_boot_notification(heartbeat_model)


async def heartbeat(cp: ChargePoint):
    logger.info(
        "Starting {} CP heartbeat background task".format(
            cp.id
        )
    )
    await cp.heartbeat()


async def start_cp(cp_model: ChargingPointModel):
    async with websockets.connect(
        uri=cp_model.ws_uri,
        subprotocols=[cp_model.protocol]
    ) as ws:
        cp = ChargePoint(id=cp_model.identity, connection=ws)
        logger.info(
            'Starting {} CP and background task'.format(cp.id)
        )
        cp_db.set_cp(cp)
        await cp.start()
