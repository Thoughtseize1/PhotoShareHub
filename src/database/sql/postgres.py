import asyncio

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.sql.models import Base, User
from src.database.sql.default_records import permissions
from src.config import settings


class Postgres:
    def __init__(self):
        user = settings.postgres_user
        pwd = settings.postgres_password
        host = settings.postgres_host
        port = settings.postgres_port
        db = settings.postgres_db
        url = (
            f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}?async_fallback=True"
        )

        self.engine = create_async_engine(url, echo=False)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        print("POSTGRES_CONNECTOR_INITIALIZED")

    async def __call__(self):
        async with self.async_session() as session:
            yield session

    async def create_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with self.async_session() as session:
            session.add_all(permissions)
            await session.commit()

    async def drop_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


database = Postgres()


async def get_user_db(session: AsyncSession = Depends(database)):
    yield SQLAlchemyUserDatabase(session, User)


async def main():
    db = Postgres()
    await db.create_database()


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
