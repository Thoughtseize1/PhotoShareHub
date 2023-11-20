"""
Comment API Routes

This module contains FastAPI routes related to comments on images.

Routes:
- create_comment: Create a new comment for an image.
- get_comment: Retrieve a specific comment by its ID.
- update_comment: Update an existing comment.
- delete_comment: Delete a comment.
"""

from fastapi import APIRouter, Path, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.sql.models import User
from src.auth.service import current_active_user
from src.comment.repository import CommentQuery
from src.image.routes import get_image
from src.comment.schemas import (
    CommentSchemaRequest,
    CommentSchemaResponse,
    CommentUpdateSchemaRequest,
)
from src.auth.utils.access import access_service
from src.database.sql.postgres import database

router = APIRouter(prefix="/comment", tags=["comments"])


@router.post(
    "/create",
    name="Create new comment",
    response_model=CommentSchemaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    body: CommentSchemaRequest,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(database),
):
    """
    Create a new comment for an image.

    :param body: CommentSchemaRequest: The comment data.
    :param user: User: The current user creating the comment.
    :param db: AsyncSession: The database session.
    :return: The created comment.
    """
    await get_image(body.image_id, user, db)
    access_service("can_add_comment", user)
    comment = await CommentQuery.create(body, user, db)
    return comment


@router.get("/{comment_id}", response_model=CommentSchemaResponse)
async def get_comment(
    comment_id: int = Path(ge=1),
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(database),
):
    """
    Get a specific comment by its ID.

    :param comment_id: int: The ID of the comment to retrieve.
    :param user: User: The current user.
    :param db: AsyncSession: The database session.
    :return: The comment if found, or raise HTTPException if not found.
    """
    comment = await CommentQuery.read(comment_id, db)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found!"
        )
    return comment


@router.put("/update/{comment_id}", response_model=CommentSchemaResponse)
async def update_comment(
    comment_id: int,
    body: CommentUpdateSchemaRequest,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(database),
):
    """
   Update an existing comment.

   :param comment_id: int: The ID of the comment to update.
   :param body: CommentUpdateSchemaRequest: The updated comment data.
   :param user: User: The current user.
   :param db: AsyncSession: The database session.
   :return: The updated comment.
   """
    comment = await CommentQuery.read(comment_id, db)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found!"
        )
    access_service("can_update_comment", user, comment)
    comment = await CommentQuery.update(comment, body, db)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int = Path(ge=1),
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(database),
):
    """
    Delete a comment.

    :param comment_id: int: The ID of the comment to delete.
    :param user: User: The current user.
    :param db: AsyncSession: The database session.
    :return: HTTP 204 No Content on success or raise HTTPException if not found.
    """
    comment = await CommentQuery.read(comment_id, db)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found!"
        )
    access_service("can_delete_comment", user, comment)
    await CommentQuery.delete(comment, db)
