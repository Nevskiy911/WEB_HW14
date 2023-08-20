from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/user_db"
    secret_key: str = "secret key"
    algorithm: str = "HS256"
    mail_username: str = "example@meta.ua"
    mail_password: str = "qwerty"
    mail_from: str = "example@meta.ua"
    mail_port: int = 465
    mail_server: str = "smtp.meta.ua"
    redis_host: str = 'localhost'
    redis_port: int = 6379

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra='ignore')

    # class Config:
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"
    #     extra = 'ignore'


config = Settings()


# class Config:
#     DB_URL = "postgresql+asyncpg://postgres:MAleXX322537@localhost:5432/user_db"
#
#
# config = Config
