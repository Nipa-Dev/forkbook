from pydantic_settings import BaseSettings
import re

TAG_PATTERN = re.compile(r"^[a-zåäö '\-]+$")


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    TAG_MAX_COUNT: int = 5
    TAG_MAX_LENGTH: int = 15

    class Config:
        env_file = ".env"


settings = Settings()


def get_database_url() -> str:
    return (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
