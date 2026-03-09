from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "UrbanPlanner"
    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/urban_planner"
    MONGO_URI: str = "mongodb://localhost:27017/urban_planner"
    REDIS_URL: str = "redis://localhost:6379/0"

    ML_SERVICE_URL: str = "http://localhost:8001"
    GEE_SERVICE_ACCOUNT: str = ""
    GEE_KEY_FILE: str = "ml/configs/gee_key.json"

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_REPORTS: str = "urban-reports"
    MINIO_BUCKET_LAYOUTS: str = "urban-layouts"

    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = "noreply@urbanplanner.in"
    SMTP_PASSWORD: str = ""

    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "urban-planner"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
