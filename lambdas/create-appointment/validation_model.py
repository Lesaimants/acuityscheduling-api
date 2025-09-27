from typing import Optional, Union
from pydantic import BaseModel


class RequestBody(BaseModel):
    datetime: str
    calendarID: Union[int, str]
    appointmentTypeID: Union[int, str]
    timezone: Optional[str] = None
    notes: Optional[str] = None
