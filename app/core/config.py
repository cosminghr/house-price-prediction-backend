from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/DeutscheTelekomAssignment"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    RATE_LIMIT: str = "10/minute"
    MODEL_PATH: str = "model.joblib"
    TRAIN_DATA: str = "housing.csv"
    RATE_LIMITER_BACKEND: str = "memory"
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
