from pydantic import BaseModel, EmailStr, Extra
from datetime import datetime
from typing import Optional,Dict,Any
from pydantic.types import conint

class LogBase(BaseModel):
    level: str
    message: str

class Log(LogBase):
    traceId: str
    spanId: str
    extra_fields: Dict[str,Any] = {}
    class Config:
        extra = Extra.allow
        orm_mode = True