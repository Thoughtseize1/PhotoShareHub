from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.sql.models import Comment, User, Image


class CommentQuery:
    """
    This module contains database queries related to comments on images.

    Functions:
        - create: Create a new comment.
        - read: Retrieve a comment by its ID.
        - update: Update a comment's text.
        - delete: Delete a comment.
    """

    @staticmethod
    async def create(body, user: User, db: AsyncSession) -> Comment:
        """
        Create a new comment.

        :param body: The comment data.
        :param user: User: The user creating the comment.
        :param db: AsyncSession: The database session.
        :return: The created comment.
        """
        comment = Comment(**body.model_dump(), owner_id=user.id)
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment

    @staticmethod
    async def read(comment_id: int, db: AsyncSession) -> Comment | None:
        """
        Read a comment by its ID.

        :param comment_id: int: The ID of the comment to retrieve.
        :param db: AsyncSession: The database session.
        :return: The comment object or None if it doesn't exist.
        """
        sq = select(Comment).filter_by(id=comment_id)
        comment = await db.execute(sq)
        comment = comment.scalar_one_or_none()
        return comment

    @staticmethod
    async def update(comment, body, db) -> Comment | None:
        """
        Update a comment's text.

        :param comment: Comment: The comment object to update.
        :param body: The updated comment text.
        :param db: The database session.
        :return: The updated comment.
        """
        comment.text = body.text
        await db.commit()
        await db.refresh(comment)
        return comment

    @staticmethod
    async def delete(comment: Comment, db: AsyncSession) -> None:
        """
        Delete a comment.

        :param comment: Comment: The comment to delete.
        :param db: AsyncSession: The database session.
        :return: None.
        """
        await db.delete(comment)
        await db.commit()
