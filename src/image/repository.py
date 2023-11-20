"""
Image Repository

This module contains database query functions related to images.

Functions:
- create: Create a new image in the database.
- read: Retrieve an image object from the database by its ID.
- update: Update an image in the database.
- delete: Delete an image from the database.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.sql.models import Image, User
from src.image.schemas import ImageSchemaUpdateRequest


class ImageQuery:
    @staticmethod
    async def create(
            title: str, cloudinary_url: str, user: User, session: AsyncSession
    ) -> Image:
        """
        Create a new image in the database.

        :param title: str: The title of the image.
        :param cloudinary_url: str: The URL of the image in Cloudinary.
        :param user: User: The user who owns the image.
        :param session: AsyncSession: The database session.
        :return: The created image object.
        """
        image = Image(title=title, owner_id=user.id, cloudinary_url=cloudinary_url)
        session.add(image)
        await session.commit()
        return image

    @staticmethod
    async def read(image_id: int, session: AsyncSession) -> Image | None:
        """
        Retrieve an image object from the database by its ID.

        :param image_id: int: The ID of the image to retrieve.
        :param session: AsyncSession: A database connection session.
        :return: An image object or None if it doesn't exist.
        """
        stmt = select(Image).where(Image.id == image_id)
        image = await session.execute(stmt)
        return image.scalars().unique().one_or_none()

    @staticmethod
    async def update(
            image: Image,
            session: AsyncSession,
            edited_cloudinary_url: str = None,
            image_data: ImageSchemaUpdateRequest = None,
    ) -> Image:
        """
        Update an image in the database.

        :param image: Image: The image object to update.
        :param session: AsyncSession: The database session.
        :param edited_cloudinary_url: str: The edited Cloudinary URL of the image.
        :param image_data: ImageSchemaUpdateRequest: Updated image data.
        :return: The updated image object.
        """
        if image_data:
            image.title = image_data.title
        if edited_cloudinary_url:
            image.edited_cloudinary_url = edited_cloudinary_url
        await session.commit()
        await session.refresh(image)
        return image

    @staticmethod
    async def delete(image: Image, session: AsyncSession) -> None:
        """
        Delete an image from the database.

        :param image: Image: The image object to delete.
        :param session: AsyncSession: The database session.
        :return: None.
        """
        await session.delete(image)
        await session.commit()
