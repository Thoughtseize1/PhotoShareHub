import os
import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from fastapi_users.db import SQLAlchemyUserDatabase
from httpx_oauth.clients.google import GoogleOAuth2
from starlette.responses import JSONResponse

from src.auth.utils.email import send_email_for_reset_pswd, send_email_verification
from src.auth.utils.send_post import send_post_request
from src.config import settings
from src.database.sql.postgres import User, get_user_db

# should be remade to get it from .env
google_oauth_client = GoogleOAuth2(
    os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
    os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", ""),
)

SECRET = settings.secret_key
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """
    User Manager Class

    This class provides user management functionality, including registration,
    password reset, and email verification.

    Attributes:
        reset_password_token_secret (str): The secret for generating reset password tokens.
        verification_token_secret (str): The secret for generating email verification tokens.

    Methods:
        on_after_register(self, user: User, request: Optional[Request] = None) -> JSONResponse:
            Perform actions after a user registers.

        on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
            Perform actions after a user requests a password reset.

        on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
            Perform actions after a user requests email verification.
    """
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Perform actions after a user registers.

        :param user (User): The registered user.
        :param request (Optional[Request]): The request object (optional).

        :return: JSONResponse: A response indicating the registration status.
        """
        print(f"User {user.id} has registered.")
        result = await send_post_request(
            request, str(user.email), "auth/request-verify-token"
        )
        return JSONResponse(result)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Perform actions after a user requests a password reset.

        :param user (User): The user who requested the password reset.
        :param token (str): The reset token.
        :param request (Optional[Request]): The request object (optional).
        """
        await send_email_for_reset_pswd(
            user.email, user.username, token, request.base_url
        )

        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Perform actions after a user requests email verification.

        :param user (User): The user who requested email verification.
        :param token (str): The verification token.
        :param request (Optional[Request]): The request object (optional).
        """
        await send_email_verification(
            user.email, user.username, token, request.base_url
        )
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """
    The get_user_manager function is a dependency provider that returns an instance of the UserManager class.
    The UserManager class is responsible for managing users in the database.
    It provides methods to create, update, and delete users as well as retrieve them by their ID or username.

    :param user_db: SQLAlchemyUserDatabase: Pass the user database instance to the function
    :return: A UserManager instance
    """
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """
    The get_jwt_strategy function returns a JWTStrategy object.
    The JWTStrategy object is initialized with the secret key and lifetime seconds arguments.
    The secret key argument is set to the value of settings.secret_key, which was imported from settings/base.py.

    :return: A JWTStrategy object
    """
    return JWTStrategy(secret=settings.secret_key, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

# add cache
current_active_user = fastapi_users.current_user(active=True)
