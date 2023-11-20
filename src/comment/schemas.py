import uuid
from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class CommentSchemaRequest(BaseModel):
    image_id: int
    text: str


class CommentUpdateSchemaRequest(BaseModel):
    text: str


class CommentSchemaResponse(CommentSchemaRequest):
    id: int
    owner_id: uuid.UUID
    image_id: int
    text: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes: True
