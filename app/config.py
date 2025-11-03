"""
Configuration settings for ECOLIFE Backend.
Uses Pydantic Settings for environment variable management.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Application
    APP_NAME: str = "ECOLIFE Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS - Allow Vercel frontend and localhost for development
    # Set ALLOWED_ORIGINS in environment as comma-separated string
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://vercel.app,https://*.vercel.app"

    def get_allowed_origins(self) -> List[str]:
        """Parse comma-separated origins from environment variable"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS

    # Database (will be configured on Day 3)
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/ecolife_db"

    # JWT Authentication (will be used on Day 2)
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Stripe (will be configured on Day 6)
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Redis (optional for Day 5)
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()
