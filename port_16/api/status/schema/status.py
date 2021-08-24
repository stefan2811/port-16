from pydantic import BaseModel


class StatusResponse(BaseModel):
    application: str
    version: str
    status: str
