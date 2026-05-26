from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'mySecretKeyForAquariumApp2026')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '43200'))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '30'))
    
    # Добавьте эти поля
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:020306@localhost:5433/aquarium_db')
    TEST_DATABASE_URL: Optional[str] = os.getenv('TEST_DATABASE_URL')
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # Игнорировать лишние поля в .env
    )

settings = Settings()