"""
Configuration settings for the Fitness  Booking API.
Centralizes all configuration management with environment variable support.
"""

import os
from typing import Optional


class Settings:
    """Application settings with environment variable support."""

    # Application Settings
    APP_NAME: str = "Fitness Studio Booking API"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fitness_studio.db")

    # Timezone Settings
    DEFAULT_TIMEZONE: str = "Asia/Kolkata"  # IST as specified in requirements

    # API Settings
    API_PREFIX: str = "/api/v1"

    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
