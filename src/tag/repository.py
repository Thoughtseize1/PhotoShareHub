"""
Tag Repository

This module defines the repository for tag-related queries.

Class:

- TagRepository: A class that provides methods for tag-related database queries.

Methods:

- create(image: Image, tag_schema: TagSchemaRequest, session: AsyncSession) -> Image:
    Creates a new image with the specified tags.

- delete(image: Image, tag_schema: TagSchemaRequest, session: AsyncSession) -> Image:
    Removes tags from an image.

- search_images_by_tags(tag_names: list[str], session: AsyncSession) -> list[Image]:
    Searches for images by tag names.
"""

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.sql.models import Tag, Image, ImageTag
from src.tag.schemas import TagSchemaRequest


class TagRepository:
    @staticmethod
    async def create(
            image: Image, tag_schema: TagSchemaRequest, session: AsyncSession
    ) -> Image:
        """
        Create a new image with specified tags.

        :param image: Image: The image object to create.
        :param tag_schema: TagSchemaRequest: The tag schema to create new tags.
        :param session: AsyncSession: The database session.
        :return: An image object.
        """
        for tag in tag_schema.names:
            stmt = select(Tag).where(Tag.name == tag)
            tag_to_append = await session.execute(stmt)
            tag_to_append = tag_to_append.scalars().unique().one_or_none()
            if tag_to_append:
                image.tags.append(tag_to_append)
            else:
                image.tags.append(Tag(name=tag))
        session.add(image)
        await session.commit()
        await session.refresh(image)
        return image

    @staticmethod
    async def delete(
            image: Image, tag_schema: TagSchemaRequest, session: AsyncSession
    ) -> Image:
        """
        Remove tags from an image.

        :param image: Image: The image object to modify.
        :param tag_schema: TagSchemaRequest: The tag schema with names to delete.
        :param session: AsyncSession: The database session.
        :return: The modified image object.
        """
        for tag in image.tags:
            if tag.name in tag_schema.names:
                image.tags.remove(tag)
        session.add(image)
        await session.commit()
        return image

    @staticmethod
    async def search_images_by_tags(tag_names: list[str], session: AsyncSession) -> list[Image]:
        """
        Search for images by tag names.

        :param tag_names: list[str]: A list of tag names to search for.
        :param session: AsyncSession: The current database session.
        :return: A list of image objects matching the tags.
        """
        stmt = (
            select(Image)
            .join(ImageTag, ImageTag.image_id == Image.id)
            .join(Tag, Tag.id == ImageTag.tag_id)
            .where(Tag.name.in_(tag_names))
            .union_all(
                select(Image).filter(Image.title.in_(tag_names))
            )
        )
        images = await session.execute(stmt)
        return images.scalars().all()
