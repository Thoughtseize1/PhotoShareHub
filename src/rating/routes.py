"""
Rating Routes

This module defines the API routes for managing ratings.

Routes:
- GET /rating/{rating_id}: Delete a rating by its ID.
- POST /rating/create: Create a new rating.
- PUT /rating/update/{rating_id}: Update an existing rating.
- DELETE /rating/delete/{rating_id}: Delete a rating.

Each route expects specific parameters and returns HTTP status codes.
"""
from fastapi import APIRouter, Depends, status, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import current_active_user
from src.database.sql.models import User
from src.database.sql.postgres import database
from src.image.routes import get_image
from src.rating.repository import RatingQuery
from src.rating.schemas import (
    RatingSchemaResponse,
    RatingSchemaRequest,
    RatingUpdateSchemaRequest,
)

router = APIRouter(prefix="/rating", tags=["ratings"])


@router.get("/{rating_id}", response_model=RatingSchemaResponse, name="Get one rating")
async def get_rating(
        rating_id: int = Path(ge=1),
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(database),
):
    """
    Get a rating by its ID.

    :param rating_id: int: The ID of the rating to retrieve.
    :param user: User: The current user obtained from authentication.
    :param db: AsyncSession: The database session.

    :return: RatingSchemaResponse: The rating object.
    """
    rating = await RatingQuery.read(rating_id, db)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found!"
        )
    return rating


@router.post(
    "/create",
    name="Add new rating",
    response_model=RatingSchemaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_rating(
        body: RatingSchemaRequest,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(database),
):
    """
    Create a new rating for an image. If the user has already rated the image,
    update their previous rating.

    :param body: RatingSchemaRequest: The rating data to create.
    :param user: User: The current user obtained from authentication.
    :param db: AsyncSession: The database session.

    :return: RatingSchemaResponse: The created or updated rating object.
    """
    image = await get_image(body.image_id, user, db)
    rating = await RatingQuery.create(body, user, image, db)
    return rating


@router.put(
    "/update/{rating_id}", response_model=RatingSchemaResponse, name="Update rating"
)
async def update_rating(
        rating_id: int,
        body: RatingUpdateSchemaRequest,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(database),
):
    """
    Update a rating by its ID.

    :param rating_id: int: The ID of the rating to update.
    :param body: RatingUpdateSchemaRequest: The updated rating data.
    :param user: User: Get the current user from authentication
    :param db: AsyncSession: The database session.

    :return: RatingSchemaResponse: The updated rating object.
    """

    rating = await RatingQuery.read(rating_id, db)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found!"
        )
    changed_rating = await RatingQuery.update(rating_id, body, user, db)
    if not changed_rating:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="This is not your rating!"
        )
    return changed_rating


@router.delete(
    "/delete/{rating_id}", status_code=status.HTTP_204_NO_CONTENT, name="Delete rating"
)
async def delete_rating(
        rating_id: int,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(database),
):
    """
        Delete a rating by its ID.

        :param rating_id: int: The ID of the rating to delete.
        :param user: User: The current user obtained from authentication.
        :param db: AsyncSession: The database session.

        :return: None
        """
    rating = await RatingQuery.read(rating_id, db)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found!"
        )
    deleted_rating = await RatingQuery.delete(rating_id, user, db)
    if not deleted_rating:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="This is not your rating!"
        )
