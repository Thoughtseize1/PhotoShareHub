import typing
import uuid
from pydantic import BaseModel, Field
from datetime import datetime


class ImageSchemaRequest(BaseModel):
    title: str = Field()


class ImageSchemaUpdateRequest(ImageSchemaRequest):
    title: str = Field(default=None)


class ImageAIReplaceTransformation(BaseModel):
    Object_to_detect: str = Field(default="")
    Replace_with: str = Field(default="")

    class Config:
        from_attributes: True


class ImageScaleTransformation(BaseModel):
    Width: int = Field(default=0)
    Height: int = Field(default=0)

    class Config:
        from_attributes: True


class ImageBlackAndWhiteTransformation(BaseModel):
    black_and_white: bool = Field(default=False)

    class Config:
        from_attributes: True


class ImageRotationTransformation(BaseModel):
    angle: int = Field(default=0, le=360, ge=-360)

    class Config:
        from_attributes: True


class EditFormData(BaseModel):
    ai_replace: typing.Optional[ImageAIReplaceTransformation] = Field(default=None)
    scale: typing.Optional[ImageScaleTransformation] = Field(default=None)
    black_and_white: typing.Optional[ImageBlackAndWhiteTransformation] = Field(
        default=None
    )
    rotation: typing.Optional[ImageRotationTransformation] = Field(default=None)


class ImageSchemaResponse(ImageSchemaRequest):
    id: int
    owner_id: uuid.UUID
    cloudinary_url: str
    edited_cloudinary_url: str | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes: True
