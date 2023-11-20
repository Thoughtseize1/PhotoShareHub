"""
Rating Repository

This module contains database query functions related to ratings.

Functions:
- _update_average_rating: Update the average rating of an image based on all available ratings.
- read: Retrieve a rating object from the database by its ID.
- create: Create a new rating for an image or update the user's previous rating.
- update: Update a rating in the database.
- delete: Delete a rating from the database.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.sql.models import User, Rating, Image
from src.image.repository import ImageQuery


class RatingQuery:
    @classmethod
    async def _update_average_rating(cls, image: Image, db: AsyncSession):
        """
        Update the average rating of an image based on all available ratings.

        :param cls: The class of the object being updated.
        :param image: Image: The image object to update.
        :param db: AsyncSession: The database session.
        :return: Nothing.
    """
        ratings = await db.execute(select(Rating).filter(Rating.image_id == image.id))
        ratings = ratings.scalars().all()
        total_rating = sum(rating.value for rating in ratings)
        average_rating = total_rating / len(ratings) if ratings else 0
        image.rating = average_rating
        await db.commit()

    @staticmethod
    async def read(rating_id: int, db: AsyncSession) -> Rating | None:
        """
        Retrieve a rating object from the database by its ID.

        :param rating_id: int: The ID of the rating to retrieve.
        :param db: AsyncSession: A database connection session.
        :return: A rating object or None if it doesn't exist.
    """
        sq = select(Rating).filter_by(id=rating_id)
        rating = await db.execute(sq)
        rating = rating.scalar_one_or_none()
        return rating

    @staticmethod
    async def create(body, user: User, image: Image, db: AsyncSession) -> Rating:
        """
        Create a new rating for an image. If the user has already rated the image,
        update their previous rating.

        :param body: Get the value of the rating.
        :param user: User: Retrieve the user object from the database.
        :param image: Image: Retrieve the image ID from the database.
        :param db: AsyncSession: Create a database session.
        :return: The rating object that was created.
    """
        rating = await db.scalar(
            select(Rating).where(
                (Rating.owner_id == user.id) & (Rating.image_id == image.id)
            )
        )
        if rating:
            rating.value = body.value
        else:
            rating = Rating(**body.model_dump(), owner_id=user.id)
        db.add(rating)
        await db.commit()
        await db.refresh(rating)
        await RatingQuery._update_average_rating(image, db)
        return rating

    @staticmethod
    async def update(rating_id: int, body, user, db) -> Rating | None:
        """
    The update function updates a rating in the database.
        It takes three arguments:
            - rating_id: The id of the rating to be updated.
            - body: A dictionary containing the new value for this Rating object.
                This is passed as an argument by FastAPI, and should not be called directly by users of this function.
            - user: The current user, which is passed as an argument by FastAPI, and should not be called directly by users of this function.

    :param rating_id: int: Identify the rating that is to be updated
    :param body: Get the new value of the rating. Schema: RatingUpdateSchemaRequest
    :param user: Check if the user is the owner of the rating
    :param db: Access the database
    :return: The updated rating or None if it doesn't exist.
    """
        rating = await db.scalar(
            select(Rating).where(
                (Rating.owner_id == user.id) & (Rating.id == rating_id)
            )
        )
        if not rating:
            return None
        rating.value = body.value
        await db.commit()
        await db.refresh(rating)
        image = await db.get(Image, rating.image_id)
        await RatingQuery._update_average_rating(image, db)
        return rating

    @staticmethod
    async def delete(rating_id: int, user, db: AsyncSession):
        """
        Delete a rating from the database.

        :param rating_id: int: Specify the ID of the rating to be deleted.
        :param user: Check if the user is the owner of the rating.
        :param db: AsyncSession: Pass in the database session.
        :return: The deleted rating or None if it doesn't exist.
    """
        rating = await db.scalar(
            select(Rating).where(
                (Rating.owner_id == user.id) & (Rating.id == rating_id)
            )
        )
        if not rating:
            return None
        await db.delete(rating)
        await db.commit()
        image = await ImageQuery.read(rating.image_id, db)
        await RatingQuery._update_average_rating(image, db)
        return rating
