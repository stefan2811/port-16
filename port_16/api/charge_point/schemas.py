from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel
from ocpp.v16.enums import Reason

WS_HOST = 'ws://localhost:8180'
WS_MAIN_PATH = '/steve/websocket/CentralSystemService/'


class ChargingPointState(Enum):
    IDLE = 'IDLE'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'


class ChargingPointModel(BaseModel):
    identity: str
    heartbeat_timeout: int = 5
    model: str = 'Dummy model'
    vendor: str = 'Some vendor'
    serial_number: str = '123456789'
    state: ChargingPointState = ChargingPointState.IDLE
    protocol: str = 'ocpp1.6'
    connector_number: int = 3
    connectors: Dict = dict()
    tags: Dict = dict()
    transactions: Dict[int, int] = dict()

    @property
    def ws_uri(self) -> str:
        return f'{WS_HOST}{WS_MAIN_PATH}{self.identity}'


class AuthorizeResponse(BaseModel):
    id_tag_info: Dict


class AuthorizeRequest(BaseModel):
    id_tag: str


class StartTransaction(BaseModel):
    connector_id: int
    id_tag: str
    meter_start: int = 20
    reservation_id: Optional[int] = None


class StopTransaction(BaseModel):
    transaction_id: int
    meter_stop: int = 10
    id_tag: Optional[str] = None
    transaction_data: Optional[List] = None
    reason: Reason = Reason.local
