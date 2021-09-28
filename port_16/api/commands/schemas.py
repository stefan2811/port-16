from typing import Dict, List, Optional

from pydantic import BaseModel
from ocpp.v16.enums import Reason


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
