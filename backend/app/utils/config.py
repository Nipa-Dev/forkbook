import re
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

TAG_PATTERN = re.compile(r"^[a-zåäö '\-]+$")
BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    PRIVATE_KEY_PATH: Path = Field(default=Path("certs/private_key.pem"))
    PUBLIC_KEY_PATH: Path = Field(default=Path("certs/public_key.pem"))

    JWT_KID: str = "dev-key-1"
    ALGORITHM: str = "RS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    EMAIL_BIDX_SECRET: str = ""

    TAG_MAX_COUNT: int = 5
    TAG_MAX_LENGTH: int = 15

    VALID_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}

    @computed_field
    @property
    def PRIVATE_KEY(self) -> str:
        """Reads and returns the content of the private key file."""
        if not self.PRIVATE_KEY_PATH.exists():
            raise FileNotFoundError(
                f"Private key file not found at: {self.PRIVATE_KEY_PATH.resolve()}"
            )
        return self.PRIVATE_KEY_PATH.read_text(encoding="utf-8")

    @computed_field
    @property
    def PUBLIC_KEY(self) -> str:
        """Reads and returns the content of the public key file."""
        if not self.PUBLIC_KEY_PATH.exists():
            raise FileNotFoundError(
                f"Public key file not found at: {self.PUBLIC_KEY_PATH.resolve()}"
            )
        return self.PUBLIC_KEY_PATH.read_text(encoding="utf-8")

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()


def get_database_path() -> str:
    return str(BASE_DIR / "data" / "app.db")
