from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RequestBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: str = "pending"


class RequestCreate(RequestBase):
    user_id: int
    category_id: int | None = None


class RequestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = None
    category_id: int | None = None


class RequestRead(RequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    category_id: int | None
    created_at: datetime
