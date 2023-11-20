"""
Image API Routes

This module contains FastAPI routes related to images.

Routes:
- get_image: Retrieve an image by its ID.
- create_image: Create a new image.
- search_image: Search for images.
- update_image: Update an image.
- delete_image: Delete an image.
- transform_image: Transform an image.
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio.client import Redis


from src.auth.service import current_active_user
from src.database.sql.postgres import database
from src.database.cache.redis_conn import cache_database
from src.database.sql.models import User
from src.image.repository import ImageQuery
from src.image.schemas import (
    ImageSchemaResponse,
    ImageSchemaUpdateRequest,
    EditFormData,
)
from src.auth.utils.access import access_service
from src.image.utils.cloudinary_service import UploadImage, ImageEditor

router = APIRouter(prefix="/image", tags=["images"])


@router.get("/{image_id}", response_model=ImageSchemaResponse)
async def get_image(
    image_id: int,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(database),
    cache: Redis = Depends(cache_database),
):
    """
    Retrieve an image by its ID.

    :param image_id: int: The ID of the image to retrieve.
    :param user: User: The current user.
    :param db: AsyncSession: The database session.
    :param cache: Redis: The Redis cache.
    :return: An image object.
    """
    image = await ImageQuery.read(image_id, db)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!"
        )
    return image


@router.post(
    "/create", response_model=ImageSchemaResponse, status_code=status.HTTP_201_CREATED
)
async def create_image(
    title: str = Form(),
    image_file: UploadFile = File(),
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(database),
    cache: Redis = Depends(cache_database),
):
    """
    Create a new image.

    :param title: str: The title of the image.
    :param image_file: UploadFile: The image file to upload.
    :param user: User: The current user.
    :param db: AsyncSession: The database session.
    :param cache: Redis: The Redis cache.
    :return: The created image object.
    """
    access_service("can_add_image", user)
    public_id = UploadImage.generate_name_folder(user)
    r = UploadImage.upload(image_file.file, public_id)
    src_url = UploadImage.get_pic_url(public_id, r)
    image = await ImageQuery.create(title, src_url, user, db)

    return image


@router.get("/search/{image_search_string}")
async def search_image(
    image_search_string: str,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(database),
    cache: Redis = Depends(cache_database),
):
    """
    Search for images.

    :param image_search_string: str: The search string.
    :param user: User: The current user.
    :param db: AsyncSession: The database session.
    :param cache: Redis: The Redis cache.
    :return: Not implemented.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/update/{image_id}", response_model=ImageSchemaResponse)
async def update_image(
    image_id: int,
    image_data: ImageSchemaUpdateRequest = None,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(database),
    cache: Redis = Depends(cache_database),
):
    """
    Update an image.

    :param image_id: int: The ID of the image to update.
    :param image_data: ImageSchemaUpdateRequest: The updated image data.
    :param user: User: The current user.
    :param db: AsyncSession: The database session.
    :param cache: Redis: The Redis cache.
    :return: The updated image object.
    """
    image = await get_image(image_id, user, db, cache)
    access_service("can_update_image", user, image)
    image = await ImageQuery.update(image, db, image_data=image_data)
    return image


@router.delete("/delete/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(database),
    cache: Redis = Depends(cache_database),
):
    """
    Delete an image.

    :param image_id: int: The ID of the image to delete.
    :param user: User: The current user.
    :param db: AsyncSession: The database session.
    :param cache: Redis: The Redis cache.
    :return: None.
    """
    image = await get_image(image_id, user, db, cache)
    access_service("can_delete_image", user, image)
    await ImageQuery.delete(image, db)


@router.post(
    "/transform/{image_id}",
    response_model=ImageSchemaResponse,
)
async def transform_image(
    image_id: int,
    transformation_data: EditFormData,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(database),
    cache: Redis = Depends(cache_database),
):
    """
    Transform an image.

    This endpoint allows users to apply transformations to an image, such as cropping, resizing, or adding filters.
    The transformed image is then stored and associated with the original image.

    :param image_id: int: The ID of the image to transform.
    :param transformation_data: EditFormData: The transformation data, including details of the desired transformations.
    :param user: User: The current user.
    :param db: AsyncSession: The database session.
    :param cache: Redis: The Redis cache.
    :return: The transformed image object.
    """
    image = await get_image(image_id, user, db, cache)
    access_service("can_update_image", user, image)
    original_img_url = image.cloudinary_url
    edited_img_url = await ImageEditor().edit_image(
        original_img_url, transformation_data
    )
    public_id = UploadImage.generate_name_folder(user, edited=True)
    r = UploadImage.upload(edited_img_url, public_id)
    edited_src_url = UploadImage.get_pic_url(public_id, r)
    image = await ImageQuery.update(image, db, edited_src_url)
    return image
