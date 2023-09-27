import uvicorn
from fastapi import FastAPI, Depends

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio.client import Redis

from src.auth.service import current_active_user
from src.database.sql.models import User
from src.database.sql.postgres import database
from src.database.cache.redis_conn import cache_database
from src.auth.utils.access import AccessService

from src.image.routes import router as images
from src.auth.routes import router as auth
from src.comment.routes import router as comments
from src.auth.utils.access import access_service

from src.tag.routes import router as tags
from src.rating.routes import router as rating

app = FastAPI()

app.include_router(auth)

app.include_router(images, prefix="/api")
app.include_router(comments, prefix="/api")
app.include_router(tags, prefix="/api")
app.include_router(rating, prefix="/api")


@app.get("/")
def read_root():
    """
    Get the root endpoint.

    Returns:
        dict: A dictionary with a single key "message" and the value "Hello World".
"""
    return {"message": "Hello World"}


@app.get("/example/healthchecker")
async def healthchecker(
    db: AsyncSession = Depends(database), cache: Redis = Depends(cache_database)
):
    """
        Check the health of the database and cache.

        :param db: AsyncSession = Depends(database): The database session.
        :param cache: Redis = Depends(cache_database): The cache database.

        :return: dict: A dictionary with a message indicating the status of the databases.
"""
    print("postgres connection check...")
    await db.execute(text("SELECT 1"))
    print("redis connection check...")
    await cache.set("1", 1)
    return {"message": "Databases are OK!"}


@app.get("/example/user-authenticated")
async def authenticated_route(user: User = Depends(current_active_user)):
    """
    The authenticated_route function is a route that requires authentication.
    It will return the email of the user and all images associated with that user.

    :param user: User: Get the user object from the database
    :return: A dictionary with the email and images of the user
"""
    print(user.images)
    return {"email": user.email, "images": user.images}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)
    #  uvicorn main:app --host localhost --port 8000
