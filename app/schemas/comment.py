from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    text: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    request_id: int


class CommentUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1)


class CommentRead(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    user_id: int
    created_at: datetime
