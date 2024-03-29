from logging import config as logging_config

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class PostgresSettings(BaseSettings):
    """Настройки Postgres."""

    echo_database: bool = Field(False, validation_alias="ECHO_DATABASE")
    postgres_host: str = Field(validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(validation_alias="POSTGRES_PORT")
    postgres_db: str = Field(validation_alias="POSTGRES_DB")
    postgres_user: str = Field(validation_alias="POSTGRES_USER")
    postgres_password: str = Field(validation_alias="POSTGRES_PASSWORD")

    @property
    def pg_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}"
            f":{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


class AppSettings(BaseSettings):
    """Настройки приложения."""

    project_name: str = Field("Barsic Bot", validation_alias="PROJECT_NAME")
    debug: bool = Field(False, validation_alias="DEBUG")

    telegram_token: SecretStr = Field(validation_alias="TELEGRAM_TOKEN")

    @property
    def user_agent(self):
        concatenated_name = self.project_name.replace(" ", "")
        return f"{concatenated_name}/1.0"


class GatewaySettings(BaseSettings):
    """Настройки гейтвеев."""

    barsic_web_gateway: str = Field("http://localhost", validation_alias="BARSIC_WEB_GATEWAY")


class Settings(AppSettings, GatewaySettings):
    """Все настройки."""

    pass


settings = Settings()
