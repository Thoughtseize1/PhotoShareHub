from pydantic import BaseModel
from typing import List


class TagSchemaRequest(BaseModel):
    image_id: int
    names: List[str]


class TagSchemaUpdateRequest(TagSchemaRequest):
    pass


class TagSchemaResponse(TagSchemaRequest):
    id: int

    class Config:
        from_attributes: True
