from pydantic import BaseModel, Field


class RequestBody(BaseModel):
    email: str
    password: str = Field(..., min_length=1)
