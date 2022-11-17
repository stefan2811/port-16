from typing import Dict

from pydantic import BaseModel


class AuthorizeResponse(BaseModel):
    id_tag_info: Dict


class AuthorizeRequest(BaseModel):
    id_tag: str
