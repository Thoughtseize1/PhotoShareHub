from fastapi import status, HTTPException

from src.database.sql.models import User, Tag, Image, Comment


class AccessService:
    def __call__(
        self, action: str, user: User, item: Image | Tag | Comment | None = None
    ):
        if item is None:
            self._check_general_access(action, user)
        else:
            self._check_operation_access(action, user, item)

    @staticmethod
    def _check_general_access(action: str, user: User):
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Email is not verified. Please varify your email: {user.email}.",
            )
        elif user.permission.__dict__.get(action, False):
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to do this operation",
            )

    @staticmethod
    def _check_operation_access(action: str, user: User, item: Image | Tag | Comment):
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Email is not verified. Please varify your email: {user.email}.",
            )
        elif (
            user.is_superuser
            or user.permission.__dict__.get(action, False)
            or user.id == item.owner_id
        ):
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not allowed to do this operation",
            )


access_service = AccessService()
