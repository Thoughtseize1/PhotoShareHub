import uuid

from pydantic import BaseModel, Field


class RatingSchemaRequest(BaseModel):
    image_id: int
    value: int = Field(ge=1, le=5)


class RatingUpdateSchemaRequest(BaseModel):
    value: int = Field(ge=1, le=5)


class RatingSchemaResponse(RatingSchemaRequest):
    id: int
    owner_id: uuid.UUID
    image_id: int
    value: int

    class Config:
        from_attributes: True
