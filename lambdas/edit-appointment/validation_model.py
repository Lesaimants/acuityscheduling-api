from typing import Optional, Union, Literal, List, Any
from pydantic import BaseModel


class RequestBody(BaseModel):
    # Required for both flows
    action: Literal["update", "reschedule"]
    appointmentId: Union[int, str]

    # For reschedule
    datetime: Optional[str] = None
    calendarID: Optional[Union[int, str]] = None
    appointmentTypeID: Optional[Union[int, str]] = None
    timezone: Optional[str] = None

    # For update
    notes: Optional[str] = None
    label: Optional[str] = None
    fields: Optional[List[Any]] = None  # Expect list of {id, value}
    admin: Optional[bool] = None
