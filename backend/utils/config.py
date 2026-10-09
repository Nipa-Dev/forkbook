import re
from pathlib import Path

from cryptography.fernet import Fernet
from pydantic import Field, SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

TAG_PATTERN = re.compile(r"^[a-zåäö '\-]+$")
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    FERNET_KEY: SecretStr = Field(..., description="Key for Fernet encryption")
    EMAIL_BIDX_SECRET: SecretStr = Field(
        ..., description="Secret key used for HMAC-SHA256 blind indexing"
    )
    PRIVATE_KEY_PATH: Path = Field(default=Path("certs/private_key.pem"))
    PUBLIC_KEY_PATH: Path = Field(default=Path("certs/public_key.pem"))

    JWT_KID: str = "dev-key-1"
    ALGORITHM: str = "RS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

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

    @field_validator("FERNET_KEY", mode="after")
    @classmethod
    def validate_fernet_key(cls, value: SecretStr) -> SecretStr:
        """Ensures the FERNET_KEY is a valid, base64-encoded 32-byte key."""
        raw_key = value.get_secret_value().encode("utf-8")
        try:
            # Instantiating Fernet verifies length and base64 encoding
            Fernet(raw_key)
        except Exception as e:
            raise ValueError(
                "Invalid FERNET_KEY. Key must be a 32-byte URL-safe base64-encoded string."
            ) from e
        return value

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


def get_database_path() -> str:
    return str(BASE_DIR / "data" / "app.db")
