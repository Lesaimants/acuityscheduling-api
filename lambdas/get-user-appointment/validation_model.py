from typing import Optional, Union
from pydantic import BaseModel


class RequestBody(BaseModel):
    calendarId: Optional[Union[int, str]] = None
    appointmentTypeId: Optional[Union[int, str]] = None
