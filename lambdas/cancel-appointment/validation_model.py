from typing import Optional, Union
from pydantic import BaseModel


class RequestBody(BaseModel):
    appointmentId: Union[int, str]
    reason: Optional[str] = None
    notifyClient: Optional[bool] = None
