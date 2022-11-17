from typing import List, Optional

from pydantic import BaseModel
from ocpp.v16.enums import Reason


class StartTransaction(BaseModel):
    connector_id: int
    id_tag: str
    start_time: str
    meter_start: int = 20
    reservation_id: Optional[int] = None


class StopTransaction(BaseModel):
    transaction_id: int
    meter_stop: int = 10
    stop_time: str
    id_tag: Optional[str] = None
    transaction_data: Optional[List] = None
    reason: Reason = Reason.local
