"""
Tag Routes

This module defines the API routes for managing tags.
Routes:

- POST /tag/create: Create a new tag.
- DELETE /tag/delete: Delete tags from an image.
- GET /tag/search: Search for images by tag name.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.sql.postgres import database
from src.database.sql.models import User
from src.auth.service import current_active_user
from src.image.repository import ImageQuery
from src.tag.schemas import TagSchemaRequest
from src.tag.repository import TagRepository
from src.image.routes import get_image
from src.auth.utils.access import access_service

router = APIRouter(prefix="/tag", tags=["tags"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_tag(
        tag_data: TagSchemaRequest,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(database),
):
    """
    Create a new tag and associate it with an image.

    :param tag_data: TagSchemaRequest: The tag schema with tag names and image_id.
    :param user: User: The current authenticated user.
    :param session: AsyncSession: The database session.
    :return: A dictionary with a "detail" message.
    """
    image = await get_image(tag_data.image_id, user, session)
    access_service("can_add_tag", user, image)
    await TagRepository.create(image, tag_data, session)
    return {"detail": "tags added"}


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tags(
        tag_data: TagSchemaRequest,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(database),
):
    """
    Delete tags from an image.

    :param tag_data: TagSchemaRequest: The tag schema with tag names and image_id.
    :param user: User: The current authenticated user.
    :param session: AsyncSession: The database session.
    :return: No content response.
    """
    image = await get_image(tag_data.image_id, user, session)
    access_service("can_delete_tag", user, image)
    await TagRepository.delete(image, tag_data, session)


@router.get("/search")
async def search_images_by_tags(tag_name: str, session: AsyncSession = Depends(database)):
    """
    Search for images by tag name.

    :param tag_name: str: The tag name to search for.

    :param session: AsyncSession: The database session.
    :raises HTTPException 404 if the tag is not found.
    :return: A list of images matching the tag.

    """

    tags = await TagRepository.search_tags(tag_name, session)
    if not tags:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tag not found')
    image_ids = [tag.image_id for tag in tags]
    images = await ImageQuery.search_images_by_tags(image_ids, session)
    return images
