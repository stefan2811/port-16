from pydantic import BaseModel
from pydantic.main import Enum

# WS_HOST = 'ws://localhost:8180'
# WS_MAIN_PATH = 'steve/websocket/CentralSystemService'
WS_HOST = 'ws://localhost:8020'
WS_MAIN_PATH = 'websocket/v16'

class HeartbeatModel(BaseModel):
    timeout: int = 5
    model: str = 'Dummy model'
    vendor: str = 'Some vendor'
    serial_number: str = '123456789'


class ChargingPointState(Enum):
    IDLE = 'IDLE'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'
    UPDATE_FIRMWARE = 'UPDATE_FIRMWARE'
    GET_DIAGNOSTICS = 'GET_DIAGNOSTICS'


class ChargingPointModel(BaseModel):
    identity: str
    protocol: str = 'ocpp1.6'
    ws_host: str = WS_HOST
    ws_path: str = WS_MAIN_PATH
    heartbeat: HeartbeatModel = HeartbeatModel()
    state: ChargingPointState = ChargingPointState.IDLE
    connector_number: int = 3

    class Config:
        use_enum_values = True

    @property
    def ws_uri(self) -> str:
        return f'{self.ws_host}/{self.ws_path}/{self.identity}'
