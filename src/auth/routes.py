from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse

from src.auth.schemas import UserRead, UserCreate, UserUpdate
from src.auth.service import auth_backend, fastapi_users, google_oauth_client, SECRET
from src.auth.utils.send_post import send_post_request

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent.parent / "templates")

router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, auth_backend, SECRET),
    prefix="/auth/google",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/user",
    tags=["user"],
)


@router.get("/auth/set_new_password/{token}", tags=["auth"])
async def reset_password_form(request: Request):
    """
    The reset_password_form function is a view function that renders the reset_password_form.html template.

    :param request: Request: Get the data from the form
    :return: The reset_password_form
"""
    return templates.TemplateResponse("reset_password_form.html", {"request": request})


@router.get("/auth/verify/{token}", tags=["auth"])
async def confirm_email(request: Request, token: str):
    """
    The confirm_email function is used to confirm a user's email address.
        It takes in the request and token as parameters, and returns a JSONResponse object.
        The function sends a POST request to the auth/verify endpoint with the token as its body,
        then returns the result of that POST request.

    :param request: Request: Get the request object from fastapi
    :param token: str: Get the token from the url
    :return: A JSONResponse with result
"""
    result = await send_post_request(request, token, "auth/verify")
    return JSONResponse(result)
