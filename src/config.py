from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    postgres_db: str = Field()
    postgres_user: str = Field()
    postgres_password: str = Field()
    postgres_port: int = Field()
    postgres_host: str = Field()

    redis_host: str = Field()
    redis_port: str = Field()

    secret_key: str = Field()
    algorithm: str = Field()

    mail_username: str = Field()
    mail_password: str = Field()
    mail_from: str = Field()
    mail_port: int = Field()
    mail_server: str = Field()
    mail_from_name: str = Field()

    cloudinary_name: str = Field()
    cloudinary_api_key: int = Field()
    cloudinary_api_secret: str = Field()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
