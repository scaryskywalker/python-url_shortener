from functools import lru_cache
from urllib.parse import urlsplit, urlunsplit

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Merchant URL Shortener", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    base_url: str = Field(default="http://localhost:8000", alias="BASE_URL")

    mysql_host: str = Field(default="localhost", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_user: str = Field(default="", alias="MYSQL_USER")
    mysql_password: str = Field(default="", alias="MYSQL_PASSWORD")
    mysql_database: str = Field(default="url_shortener_db", alias="MYSQL_DATABASE")

    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_url_env: str | None = Field(default=None, alias="REDIS_URL")

    api_rate_limit_per_minute: int = Field(default=100, alias="API_RATE_LIMIT_PER_MINUTE")
    redis_short_url_cache_seconds: int = Field(default=3600, alias="REDIS_SHORT_URL_CACHE_SECONDS")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def redis_url(self) -> str:
        if self.redis_url_env:
            return self.redis_url_env
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def public_base_url(self) -> str:
        value = self.base_url.strip().rstrip("/")
        while value.startswith("https:https://"):
            value = "https://" + value[len("https:https://") :]
        while value.startswith("http:http://"):
            value = "http://" + value[len("http:http://") :]
        parsed = urlsplit(value)
        if not parsed.scheme:
            value = f"https://{value}"
            parsed = urlsplit(value)
        if parsed.path in ("", "/"):
            return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
