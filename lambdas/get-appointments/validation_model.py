from typing import Optional, Literal
from pydantic import BaseModel


class RequestBody(BaseModel):
    resource: Literal["appointments", "availability"]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    date: Optional[str] = None
    calendarId: Optional[str] = None
    appointmentTypeId: Optional[str] = None
    timezone: Optional[str] = None
    limit: Optional[int] = None
    page: Optional[int] = None
