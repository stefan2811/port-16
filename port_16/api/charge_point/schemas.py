from enum import Enum

from pydantic import BaseModel

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

    @property
    def ws_uri(self) -> str:
        return f'{WS_HOST}{WS_MAIN_PATH}{self.identity}'
