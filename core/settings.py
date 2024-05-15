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


class RedisSettings(BaseSettings):
    """Настройки Redis."""

    redis_host: str = Field("127.0.0.1", validation_alias="REDIS_HOST")
    redis_port: int = Field(6379, validation_alias="REDIS_PORT")
    cache_time: int = Field(60 * 60 * 24 * 30, validation_alias="CACHE_TIME")


class AppSettings(BaseSettings):
    """Настройки приложения."""

    project_name: str = Field("Barsic Bot", validation_alias="PROJECT_NAME")
    debug: bool = Field(False, validation_alias="DEBUG")

    bot_telegram_token: SecretStr = Field(validation_alias="BOT_TELEGRAM_TOKEN")
    user_password: SecretStr = Field(validation_alias="USER_PASSWORD")
    admin_password: SecretStr = Field(validation_alias="ADMIN_PASSWORD")
    password_limit: int = Field(10, validation_alias="WRITE_PASSWORD_LIMIT_PER_DAY")
    checkbox_size: int = Field(10, validation_alias="CHECKBOX_SIZE")

    @property
    def user_agent(self):
        concatenated_name = self.project_name.replace(" ", "")
        return f"{concatenated_name}/1.0"


class GatewaySettings(BaseSettings):
    """Настройки гейтвеев."""

    barsic_web_host: str = Field("localhost", validation_alias="BARSIC_WEB_HOST")
    barsic_web_port: int = Field(80, validation_alias="BARSIC_WEB_PORT")

    @property
    def barsic_web_gateway(self) -> str:
        return f"http://{self.barsic_web_host}:{self.barsic_web_port}"


class Settings(AppSettings, GatewaySettings, RedisSettings):
    """Все настройки."""

    pass


settings = Settings()
