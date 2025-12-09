from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB
    DATABASE_URL: str = "sqlite:///./app.db"

    # JWT
    JWT_SECRET_KEY: str = "kb3x29r8-2af0-41d4-9e41-83d8acfb02cd"  # 🔥 고정된 UUID 적용
    JWT_REFRESH_SECRET_KEY: str = "0ee2ab4c-75f5-42f0-9b42-1a8c151a3d99"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 🔥 1시간 유지
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
